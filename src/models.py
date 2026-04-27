"""Model definitions for every stage of the project.

* ``build_face_model``         - Face-only ResNet18 (Part 1, Part 2)
* ``build_full_image_model``   - Frozen ResNet50 backbone + MLP head (Part 3)
* ``FusionMLP``                - Late-fusion classifier over face+image+meta (Part 4)
* ``CLIPMultimodalClassifier`` - HuggingFace CLIP image+text fusion (Extra credit)
"""
from __future__ import annotations

from typing import Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models

from . import config as C


# -------------------------------------------------------------------------
# Part 1 / Part 2 -- face-only ResNet18
# -------------------------------------------------------------------------
def build_face_model(num_classes: int = C.NUM_CLASSES, pretrained: bool = True) -> nn.Module:
    """ResNet18 with the final FC swapped to ``num_classes``.

    All layers stay trainable -- the face dataset is small enough that
    fine-tuning the whole net is faster to convergence than a frozen
    backbone, and we already use pretrained ImageNet weights.
    """
    weights = models.ResNet18_Weights.IMAGENET1K_V1 if pretrained else None
    model = models.resnet18(weights=weights)
    in_features = model.fc.in_features
    model.fc = nn.Linear(in_features, num_classes)
    return model


# -------------------------------------------------------------------------
# Part 3 -- full-image, frozen ResNet50 + MLP head
# -------------------------------------------------------------------------
class FrozenBackboneMLP(nn.Module):
    """Frozen feature extractor (ResNet50 by default) + custom MLP head.

    The brief mandates a frozen backbone for the full-image stage, so we
    set ``requires_grad=False`` on every backbone parameter and put it in
    eval mode so BatchNorm running stats are not updated during training.
    """

    def __init__(
        self,
        num_classes: int = C.NUM_CLASSES,
        backbone: str = "resnet50",
        feature_dim: Optional[int] = None,
        hidden_dims: Tuple[int, int] = (512, 128),
        dropout: Tuple[float, float] = (0.3, 0.2),
    ) -> None:
        super().__init__()
        self.backbone_name = backbone
        self.feature_extractor, feat_dim = self._build_backbone(backbone)
        if feature_dim is None:
            feature_dim = feat_dim

        # Freeze
        for p in self.feature_extractor.parameters():
            p.requires_grad = False

        h1, h2 = hidden_dims
        d1, d2 = dropout
        self.classifier = nn.Sequential(
            nn.Linear(feature_dim, h1),
            nn.ReLU(inplace=True),
            nn.Dropout(d1),
            nn.Linear(h1, h2),
            nn.ReLU(inplace=True),
            nn.Dropout(d2),
            nn.Linear(h2, num_classes),
        )

    @staticmethod
    def _build_backbone(name: str) -> Tuple[nn.Module, int]:
        name = name.lower()
        if name == "resnet50":
            net = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)
            feat_dim = net.fc.in_features
            net.fc = nn.Identity()
            return net, feat_dim
        if name == "resnet18":
            net = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
            feat_dim = net.fc.in_features
            net.fc = nn.Identity()
            return net, feat_dim
        if name == "vit_b_16":
            net = models.vit_b_16(weights=models.ViT_B_16_Weights.IMAGENET1K_V1)
            feat_dim = net.heads.head.in_features
            net.heads.head = nn.Identity()
            return net, feat_dim
        raise ValueError(f"Unknown backbone: {name}")

    def train(self, mode: bool = True):
        # Keep backbone in eval mode so BN/Dropout stats stay frozen.
        super().train(mode)
        self.feature_extractor.eval()
        return self

    @torch.no_grad()
    def extract_features(self, x: torch.Tensor) -> torch.Tensor:
        return self.feature_extractor(x)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        feats = self.extract_features(x)
        return self.classifier(feats)


def build_full_image_model(
    backbone: str = "resnet50",
    num_classes: int = C.NUM_CLASSES,
) -> FrozenBackboneMLP:
    return FrozenBackboneMLP(num_classes=num_classes, backbone=backbone)


# -------------------------------------------------------------------------
# Part 4 -- late fusion MLP
# -------------------------------------------------------------------------
class FusionMLP(nn.Module):
    """Combines face probs + image probs + face count + flag.

    Input vector layout (8 dims):
        [face_p_neg, face_p_neu, face_p_pos,
         img_p_neg,  img_p_neu,  img_p_pos,
         num_faces_normalised, face_detected_flag]
    """

    INPUT_DIM = 8

    def __init__(self, num_classes: int = C.NUM_CLASSES, dropout: float = 0.2) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(self.INPUT_DIM, 32),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(32, 16),
            nn.ReLU(inplace=True),
            nn.Linear(16, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


# -------------------------------------------------------------------------
# Extra credit -- CLIP image+text multimodal
# -------------------------------------------------------------------------
class CLIPMultimodalClassifier(nn.Module):
    """Frozen CLIP image+text encoders -> concat -> MLP classifier.

    Uses HuggingFace ``transformers.CLIPModel`` so tokenisation and
    image processing are handled by the matched processor. The encoders
    are frozen by default; you can call ``unfreeze_last_layer()`` for an
    optional final fine-tuning pass.
    """

    def __init__(
        self,
        clip_model_name: str = "openai/clip-vit-base-patch32",
        num_classes: int = C.NUM_CLASSES,
        hidden_dim: int = 256,
        dropout: float = 0.2,
        freeze_encoders: bool = True,
    ) -> None:
        super().__init__()
        from transformers import CLIPModel

        self.clip = CLIPModel.from_pretrained(clip_model_name)
        if freeze_encoders:
            for p in self.clip.parameters():
                p.requires_grad = False
            self.clip.eval()

        img_dim = self.clip.config.projection_dim
        txt_dim = self.clip.config.projection_dim
        self.classifier = nn.Sequential(
            nn.Linear(img_dim + txt_dim, hidden_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout / 2),
            nn.Linear(hidden_dim // 2, num_classes),
        )

    def train(self, mode: bool = True):
        super().train(mode)
        # Keep CLIP in eval mode unless explicitly unfrozen.
        if not any(p.requires_grad for p in self.clip.parameters()):
            self.clip.eval()
        return self

    def unfreeze_last_layer(self) -> None:
        """Unfreeze the last transformer block of both encoders for fine-tuning."""
        # Vision tower
        v_layers = self.clip.vision_model.encoder.layers
        for p in v_layers[-1].parameters():
            p.requires_grad = True
        # Text tower
        t_layers = self.clip.text_model.encoder.layers
        for p in t_layers[-1].parameters():
            p.requires_grad = True

    @staticmethod
    def _as_tensor(out) -> torch.Tensor:
        # transformers >=5 returns BaseModelOutputWithPooling (projected
        # features in .pooler_output); older versions returned a tensor.
        if isinstance(out, torch.Tensor):
            return out
        if hasattr(out, "pooler_output"):
            return out.pooler_output
        return out[0]

    def encode_image(self, pixel_values: torch.Tensor) -> torch.Tensor:
        out = self.clip.get_image_features(pixel_values=pixel_values)
        return F.normalize(self._as_tensor(out), dim=-1)

    def encode_text(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        out = self.clip.get_text_features(input_ids=input_ids, attention_mask=attention_mask)
        return F.normalize(self._as_tensor(out), dim=-1)

    def forward(
        self,
        pixel_values: torch.Tensor,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
    ) -> torch.Tensor:
        img_feat = self.encode_image(pixel_values)
        txt_feat = self.encode_text(input_ids, attention_mask)
        fused = torch.cat([img_feat, txt_feat], dim=-1)
        return self.classifier(fused)
