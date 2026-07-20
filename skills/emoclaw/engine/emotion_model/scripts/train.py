"""Training script for EmotionModel.

Trains the model on labeled emotional data with weighted MSE loss.
Saves the best checkpoint based on validation loss.

Two checkpoint types:
  - best_model.pt / rel_embeddings.pt — inference weights only
  - training_checkpoint.pt — rich dict for resuming training

Usage:
    python -m emotion_model.scripts.train [--epochs 100] [--lr 1e-3]
    python -m emotion_model.scripts.train --resume          # resume from last checkpoint
    python -m emotion_model.scripts.train --resume path.pt  # resume from specific file
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from emotion_model import config
from emotion_model.model import EmotionModel
from emotion_model.encoder import TextEncoder
from emotion_model.features import RelationshipEmbeddings


class EmotionDataset(Dataset):
    """Dataset of labeled emotional examples."""

    def __init__(self, data_path: Path, encoder: TextEncoder) -> None:
        self.encoder = encoder
        self.examples: list[dict] = []

        with open(data_path) as f:
            for line in f:
                if line.strip():
                    self.examples.append(json.loads(line))

    def __len__(self) -> int:
        return len(self.examples)

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        ex = self.examples[idx]

        # Encode text
        text = ex["message_text"]
        context = ex.get("context")
        text_embed = self.encoder.encode_with_context(text, context)

        # Previous emotion (use baseline if not specified)
        prev = ex.get("prev_emotion", config.BASELINE_EMOTION)
        prev_emotion = torch.tensor(prev, dtype=torch.float32)

        # Target emotion vector
        target = torch.tensor(ex["emotion_vector"], dtype=torch.float32)

        return text_embed, prev_emotion, target


class WeightedEmotionLoss(nn.Module):
    """Weighted MSE loss with higher weight on critical dimensions."""

    def __init__(self) -> None:
        super().__init__()
        self.dim_weights = torch.tensor(config.DIM_LOSS_WEIGHTS, dtype=torch.float32)

    def forward(self, pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        weights = self.dim_weights.to(pred.device)
        mse = (pred - target) ** 2
        return (mse * weights).mean()


# ---------------------------------------------------------------------------
# Checkpoint helpers
# ---------------------------------------------------------------------------


def _save_training_checkpoint(
    path: Path,
    epoch: int,
    model: EmotionModel,
    rel_embeddings: RelationshipEmbeddings,
    optimizer: torch.optim.Optimizer,
    scheduler: torch.optim.lr_scheduler.LRScheduler,
    best_val_loss: float,
    patience_counter: int,
) -> None:
    """Save a rich training checkpoint for full resume."""
    torch.save(
        {
            "epoch": epoch,
            "model_state_dict": model.state_dict(),
            "rel_embeddings_state_dict": rel_embeddings.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "scheduler_state_dict": scheduler.state_dict(),
            "best_val_loss": best_val_loss,
            "patience_counter": patience_counter,
            "config_num_dims": config.NUM_EMOTION_DIMS,
        },
        path,
    )


def _load_training_checkpoint(path: Path) -> dict:
    """Load a rich training checkpoint, validating dimensions."""
    checkpoint = torch.load(path, map_location="cpu", weights_only=False)

    # Validate dimension compatibility
    saved_dims = checkpoint.get("config_num_dims")
    if saved_dims is not None and saved_dims != config.NUM_EMOTION_DIMS:
        raise RuntimeError(
            f"Checkpoint was trained with {saved_dims} emotion dimensions "
            f"but current config has {config.NUM_EMOTION_DIMS}. "
            f"You must retrain from scratch or update your config."
        )

    return checkpoint


def _save_inference_weights(
    model: EmotionModel,
    rel_embeddings: RelationshipEmbeddings,
) -> None:
    """Save simple inference-only weights (best_model.pt + rel_embeddings.pt)."""
    torch.save(model.state_dict(), config.CHECKPOINT_DIR / "best_model.pt")
    torch.save(rel_embeddings.state_dict(), config.CHECKPOINT_DIR / "rel_embeddings.pt")


# ---------------------------------------------------------------------------
# Main training loop
# ---------------------------------------------------------------------------


def train(
    epochs: int = config.TRAIN_EPOCHS,
    lr: float = config.TRAIN_LR,
    batch_size: int = config.TRAIN_BATCH_SIZE,
    resume_from: str | None = None,
) -> None:
    data_dir = config.DATA_DIR
    train_path = data_dir / "train.jsonl"
    val_path = data_dir / "val.jsonl"

    if not train_path.exists():
        print("No training data found. Run prepare_dataset.py first.")
        return

    print("Loading text encoder...")
    encoder = TextEncoder()

    print("Loading datasets...")
    train_dataset = EmotionDataset(train_path, encoder)
    val_dataset = EmotionDataset(val_path, encoder) if val_path.exists() else None

    print(f"  Train: {len(train_dataset)} examples")
    if val_dataset:
        print(f"  Val:   {len(val_dataset)} examples")

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = (
        DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
        if val_dataset
        else None
    )

    # Initialize model
    model = EmotionModel()
    rel_embeddings = RelationshipEmbeddings()

    # Training setup
    all_params = list(model.parameters()) + list(rel_embeddings.parameters())
    criterion = WeightedEmotionLoss()
    optimizer = torch.optim.AdamW(all_params, lr=lr, weight_decay=config.TRAIN_WEIGHT_DECAY)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    # Resume state
    start_epoch = 0
    best_val_loss = float("inf")
    patience_counter = 0

    if resume_from:
        resume_path = Path(resume_from)
        if not resume_path.exists():
            print(f"Warning: Checkpoint not found at {resume_path}, training from scratch.")
        else:
            print(f"Resuming from {resume_path}...")
            checkpoint = _load_training_checkpoint(resume_path)

            model.load_state_dict(checkpoint["model_state_dict"])
            rel_embeddings.load_state_dict(checkpoint["rel_embeddings_state_dict"])
            optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
            scheduler.load_state_dict(checkpoint["scheduler_state_dict"])
            start_epoch = checkpoint["epoch"] + 1
            best_val_loss = checkpoint["best_val_loss"]
            patience_counter = checkpoint["patience_counter"]

            print(f"  Resumed at epoch {start_epoch}, best_val_loss={best_val_loss:.4f}")

    patience = config.TRAIN_PATIENCE

    config.CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"\nTraining for {epochs} epochs (starting at {start_epoch})...")
    print(f"  LR: {lr}, Batch size: {batch_size}, Patience: {patience}")
    print(f"  Model params: {sum(p.numel() for p in model.parameters()):,}")
    print()

    for epoch in range(start_epoch, epochs):
        # --- Train ---
        model.train()
        train_loss = 0.0
        for text_embed, prev_emotion, target in train_loader:
            optimizer.zero_grad()

            # Use zero context features during training (simplified)
            # In production, context features come from ConversationContext
            context_features = torch.zeros(text_embed.size(0), config.CONTEXT_DIM)

            emotion, _ = model(text_embed, context_features, prev_emotion)
            loss = criterion(emotion, target)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(all_params, config.GRAD_CLIP)
            optimizer.step()
            train_loss += loss.item()

        avg_train = train_loss / max(len(train_loader), 1)

        # --- Validate ---
        avg_val = float("inf")
        if val_loader:
            model.train(False)  # inference mode
            val_loss = 0.0
            with torch.no_grad():
                for text_embed, prev_emotion, target in val_loader:
                    context_features = torch.zeros(text_embed.size(0), config.CONTEXT_DIM)
                    emotion, _ = model(text_embed, context_features, prev_emotion)
                    loss = criterion(emotion, target)
                    val_loss += loss.item()
            avg_val = val_loss / max(len(val_loader), 1)

        scheduler.step()

        # --- Checkpoint ---
        if avg_val < best_val_loss:
            best_val_loss = avg_val
            patience_counter = 0
            _save_inference_weights(model, rel_embeddings)
        else:
            patience_counter += 1

        # Always save training checkpoint (enables resume from any point)
        _save_training_checkpoint(
            config.CHECKPOINT_DIR / "training_checkpoint.pt",
            epoch=epoch,
            model=model,
            rel_embeddings=rel_embeddings,
            optimizer=optimizer,
            scheduler=scheduler,
            best_val_loss=best_val_loss,
            patience_counter=patience_counter,
        )

        # --- Logging ---
        if (epoch + 1) % 10 == 0 or epoch == start_epoch:
            print(
                f"  Epoch {epoch+1:3d}/{epochs}  "
                f"train_loss={avg_train:.4f}  "
                f"val_loss={avg_val:.4f}  "
                f"best={best_val_loss:.4f}  "
                f"lr={scheduler.get_last_lr()[0]:.6f}"
            )

        # Early stopping
        if patience_counter >= patience:
            print(f"\n  Early stopping at epoch {epoch+1} (patience={patience})")
            break

    # Save final checkpoint
    torch.save(model.state_dict(), config.CHECKPOINT_DIR / "final_model.pt")

    print(f"\nTraining complete.")
    print(f"  Best validation loss: {best_val_loss:.4f}")
    print(f"  Best model: {config.CHECKPOINT_DIR / 'best_model.pt'}")
    print(f"  Training checkpoint: {config.CHECKPOINT_DIR / 'training_checkpoint.pt'}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Train EmotionModel")
    parser.add_argument("--epochs", type=int, default=config.TRAIN_EPOCHS)
    parser.add_argument("--lr", type=float, default=config.TRAIN_LR)
    parser.add_argument("--batch-size", type=int, default=config.TRAIN_BATCH_SIZE)
    parser.add_argument(
        "--resume",
        nargs="?",
        const="auto",
        default=None,
        help="Resume training (no arg = auto-find checkpoint, or specify path)",
    )
    args = parser.parse_args()

    # Resolve resume path
    resume_from = None
    if args.resume == "auto":
        auto_path = config.CHECKPOINT_DIR / "training_checkpoint.pt"
        if auto_path.exists():
            resume_from = str(auto_path)
        else:
            print(f"No training checkpoint found at {auto_path}, training from scratch.")
    elif args.resume is not None:
        resume_from = args.resume

    train(
        epochs=args.epochs,
        lr=args.lr,
        batch_size=args.batch_size,
        resume_from=resume_from,
    )


if __name__ == "__main__":
    main()
