"""
Loads the trained WelfareClassifierNet (if it exists) and exposes a single
classify(text) function. If the model hasn't been trained yet (files
missing), is_available() returns False and the caller should fall back to
risk_classifier.rule_based_classify — the app is designed to degrade
gracefully either way.

is_available() also checks that the saved labels match config.CATEGORIES /
config.SEVERITY_LEVELS exactly (same set). Without this, if the app is ever
retrained with a different category list (this project already went from 6
to 8 categories once, per README.md) but an old welfare_classifier.pt /
welfare_classifier_labels.json pair is left over from before, is_available()
would still return True. The model would then load successfully but predict
from its OLD label set, and the mismatch would only surface as a wrong or
crashing answer on the first real student message, not at startup where it
would be easy to notice and fix.
"""
import json
import os

import torch

import config
from classifier_model import WelfareClassifierNet

_model = None
_embedder = None
_categories = None
_severities = None


def is_available() -> bool:
    """True only if the model files exist AND their saved label set still
    matches config.py. A stale model (trained under an old category list)
    is treated as unavailable, so the app falls back to
    risk_classifier.rule_based_classify instead of loading a model whose
    outputs no longer line up with the rest of the app — the same
    "degrade gracefully" behaviour as a missing model, applied to a
    mismatched one too."""
    if not (os.path.exists(config.CLASSIFIER_MODEL_PATH) and os.path.exists(config.CLASSIFIER_LABELS_PATH)):
        return False
    try:
        with open(config.CLASSIFIER_LABELS_PATH) as f:
            labels = json.load(f)
        saved_categories = set(labels.get("categories", []))
        saved_severities = set(labels.get("severities", []))
    except (json.JSONDecodeError, OSError):
        return False   # unreadable/corrupt labels file -- treat as unavailable, not a crash

    current_categories = set(config.CATEGORIES)
    # The model never learns "Critical" (see classifier_model.py's docstring),
    # so its severities are a strict subset of config.SEVERITY_LEVELS, not an
    # exact match.
    current_severities = set(config.SEVERITY_LEVELS)

    if saved_categories != current_categories:
        print(f"[neural_classifier] Stale model: trained on {sorted(saved_categories)}, "
              f"but config.CATEGORIES is now {sorted(current_categories)}. "
              "Falling back to rule-based classification -- run train_classifier.py to retrain.")
        return False
    if not saved_severities or not saved_severities.issubset(current_severities):
        print(f"[neural_classifier] Stale model: trained on severities {sorted(saved_severities)}, "
              f"which don't fit config.SEVERITY_LEVELS {sorted(current_severities)}. "
              "Falling back to rule-based classification -- run train_classifier.py to retrain.")
        return False
    return True


def _load():
    global _model, _embedder, _categories, _severities
    if _model is not None:
        return

    with open(config.CLASSIFIER_LABELS_PATH) as f:
        labels = json.load(f)
    _categories = labels["categories"]
    _severities = labels["severities"]

    _model = WelfareClassifierNet(len(_categories), len(_severities))
    _model.load_state_dict(torch.load(config.CLASSIFIER_MODEL_PATH, map_location="cpu"))
    _model.eval()

    from langchain_huggingface import HuggingFaceEmbeddings
    _embedder = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL_NAME)


def classify(text: str):
    """Returns (category, severity, confidence) using the trained model.
    confidence is the softmax probability of the predicted category —
    useful for deciding whether to trust the model or fall back."""
    _load()
    embedding = torch.tensor([_embedder.embed_query(text)], dtype=torch.float32)
    with torch.no_grad():
        cat_logits, sev_logits = _model(embedding)
        cat_probs = torch.softmax(cat_logits, dim=1)[0]
        sev_probs = torch.softmax(sev_logits, dim=1)[0]

    cat_idx = int(cat_probs.argmax())
    sev_idx = int(sev_probs.argmax())
    confidence = float(cat_probs[cat_idx])

    return _categories[cat_idx], _severities[sev_idx], confidence


def classify_full(text: str):
    """Like classify(), but also returns P(High severity) so the app can
    escalate on a *probability* rather than only the top prediction (the
    severity head misses many High cases as its argmax).
    Returns (category, severity, confidence, p_high)."""
    _load()
    embedding = torch.tensor([_embedder.embed_query(text)], dtype=torch.float32)
    with torch.no_grad():
        cat_logits, sev_logits = _model(embedding)
        cat_probs = torch.softmax(cat_logits, dim=1)[0]
        sev_probs = torch.softmax(sev_logits, dim=1)[0]

    cat_idx = int(cat_probs.argmax())
    sev_idx = int(sev_probs.argmax())
    p_high = float(sev_probs[_severities.index("High")]) if "High" in _severities else None
    return _categories[cat_idx], _severities[sev_idx], float(cat_probs[cat_idx]), p_high