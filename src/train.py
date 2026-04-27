"""Generic training loop used by every notebook.

Designed to be small enough to read in one sitting but flexible enough
to handle: face model, full-image model, fusion MLP and CLIP multimodal.
The trainer is model-agnostic -- callers supply the model, dataloaders
and a ``forward_fn`` that knows how to unpack a batch.
"""
from __future__ import annotations

import copy
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple, Union

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from tqdm.auto import tqdm

from . import config as C
from .config import TrainConfig
from .utils import get_device


# -------------------------------------------------------------------------
# Forward-fn helpers
# -------------------------------------------------------------------------
def default_forward(model: nn.Module, batch, device: torch.device):
    """Single-image classifier: batch == (images, labels, sample_ids)."""
    images, labels, _ = batch
    images = images.to(device, non_blocking=True)
    labels = labels.to(device, non_blocking=True)
    logits = model(images)
    return logits, labels


def fusion_forward(model: nn.Module, batch, device: torch.device):
    """Fusion MLP: batch == (feature_vector, label)."""
    feats, labels = batch
    feats = feats.to(device, non_blocking=True)
    labels = labels.to(device, non_blocking=True)
    logits = model(feats)
    return logits, labels


def clip_forward_factory(processor):
    """Build a forward-fn for CLIP that tokenises text via the matched processor."""
    def _fwd(model, batch, device):
        images, texts, labels, _ = batch
        images = images.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)
        # Tokenise text on the fly so DataLoaders stay simple
        tok = processor.tokenizer(
            list(texts),
            padding=True, truncation=True, max_length=64, return_tensors="pt",
        )
        input_ids = tok["input_ids"].to(device, non_blocking=True)
        attn = tok["attention_mask"].to(device, non_blocking=True)
        logits = model(images, input_ids, attn)
        return logits, labels
    return _fwd


# -------------------------------------------------------------------------
# Trainer
# -------------------------------------------------------------------------
@dataclass
class History:
    train_loss: List[float] = field(default_factory=list)
    val_loss: List[float] = field(default_factory=list)
    train_acc: List[float] = field(default_factory=list)
    val_acc: List[float] = field(default_factory=list)
    epoch_time: List[float] = field(default_factory=list)

    def to_dict(self) -> Dict[str, List[float]]:
        return {
            "train_loss": self.train_loss,
            "val_loss": self.val_loss,
            "train_acc": self.train_acc,
            "val_acc": self.val_acc,
            "epoch_time": self.epoch_time,
        }


def _accuracy(logits: torch.Tensor, labels: torch.Tensor) -> float:
    preds = logits.argmax(dim=1)
    return (preds == labels).float().mean().item()


def run_epoch(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    optimizer: Optional[torch.optim.Optimizer],
    device: torch.device,
    forward_fn: Callable = default_forward,
    grad_clip: Optional[float] = 1.0,
    train: bool = True,
    desc: str = "",
) -> Tuple[float, float]:
    model.train(mode=train)
    total_loss = 0.0
    total_correct = 0
    total_seen = 0
    pbar = tqdm(loader, leave=False, desc=desc)
    for batch in pbar:
        if train and optimizer is not None:
            optimizer.zero_grad(set_to_none=True)

        with torch.set_grad_enabled(train):
            logits, labels = forward_fn(model, batch, device)
            loss = criterion(logits, labels)
            if train:
                loss.backward()
                if grad_clip is not None:
                    nn.utils.clip_grad_norm_(
                        [p for p in model.parameters() if p.requires_grad], grad_clip,
                    )
                if optimizer is not None:
                    optimizer.step()

        bs = labels.size(0)
        total_loss += loss.item() * bs
        total_correct += (logits.argmax(dim=1) == labels).sum().item()
        total_seen += bs
        pbar.set_postfix(loss=f"{loss.item():.4f}", acc=f"{total_correct/total_seen:.3f}")

    return total_loss / max(1, total_seen), total_correct / max(1, total_seen)


def train_classifier(
    model: nn.Module,
    train_loader: DataLoader,
    val_loader: DataLoader,
    cfg: TrainConfig = TrainConfig(),
    criterion: Optional[nn.Module] = None,
    optimizer: Optional[torch.optim.Optimizer] = None,
    scheduler: Optional[torch.optim.lr_scheduler._LRScheduler] = None,
    forward_fn: Callable = default_forward,
    save_path: Optional[Union[str, Path]] = None,
    class_weights: Optional[torch.Tensor] = None,
) -> Tuple[nn.Module, History]:
    """Train ``model`` with early stopping on validation loss.

    Returns the model loaded with the best validation weights and the
    history object for plotting.
    """
    device = get_device(cfg.device)
    model = model.to(device)

    if criterion is None:
        if class_weights is not None:
            criterion = nn.CrossEntropyLoss(
                weight=class_weights.to(device),
                label_smoothing=cfg.label_smoothing,
            )
        else:
            criterion = nn.CrossEntropyLoss(label_smoothing=cfg.label_smoothing)

    if optimizer is None:
        params = [p for p in model.parameters() if p.requires_grad]
        optimizer = torch.optim.AdamW(params, lr=cfg.lr, weight_decay=cfg.weight_decay)

    if scheduler is None:
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=cfg.epochs)

    history = History()
    best_val_loss = float("inf")
    best_state = None
    epochs_without_improve = 0

    for epoch in range(1, cfg.epochs + 1):
        t0 = time.time()
        tr_loss, tr_acc = run_epoch(
            model, train_loader, criterion, optimizer, device,
            forward_fn=forward_fn, grad_clip=cfg.grad_clip, train=True,
            desc=f"Ep{epoch}/{cfg.epochs} train",
        )
        val_loss, val_acc = run_epoch(
            model, val_loader, criterion, optimizer=None, device=device,
            forward_fn=forward_fn, grad_clip=None, train=False,
            desc=f"Ep{epoch}/{cfg.epochs}  val ",
        )
        scheduler.step()

        history.train_loss.append(tr_loss); history.train_acc.append(tr_acc)
        history.val_loss.append(val_loss); history.val_acc.append(val_acc)
        history.epoch_time.append(time.time() - t0)

        print(
            f"[Epoch {epoch:02d}] "
            f"train_loss={tr_loss:.4f} train_acc={tr_acc:.3f}  "
            f"val_loss={val_loss:.4f} val_acc={val_acc:.3f}  "
            f"({history.epoch_time[-1]:.1f}s)"
        )

        if val_loss < best_val_loss - 1e-4:
            best_val_loss = val_loss
            best_state = copy.deepcopy(model.state_dict())
            epochs_without_improve = 0
            if save_path is not None:
                save_path = Path(save_path)
                save_path.parent.mkdir(parents=True, exist_ok=True)
                torch.save(best_state, save_path)
        else:
            epochs_without_improve += 1
            if epochs_without_improve >= cfg.early_stop_patience:
                print(f"Early stopping at epoch {epoch} (no improvement for "
                      f"{cfg.early_stop_patience} epochs).")
                break

    if best_state is not None:
        model.load_state_dict(best_state)
    return model, history
