"""
AI-based severity prediction (spec item 2).

predict_severity(text) -> (severity: "high"|"medium"|"low", confidence: float)

Resolution order:
  1. If settings.SEVERITY_ENGINE == "gemini" and an API key is configured,
     try calling the Gemini API. Any failure (missing package, no network,
     bad response) silently falls back to step 2.
  2. Local, offline scikit-learn model trained by train_severity_model.py
     (ships pre-trained in severity_model.joblib - no setup required).
  3. If the model file is somehow missing, a simple keyword-weighted
     rule-based scorer so the feature never hard-fails.
"""

from pathlib import Path

MODEL_PATH = Path(__file__).resolve().parent / "severity_model.joblib"

_pipeline = None
_pipeline_loaded = False

HIGH_KEYWORDS = [
    "fire", "shock", "spark", "gas leak", "theft", "stolen", "unsafe",
    "harass", "fell", "fall", "injury", "injured", "blood", "unconscious",
    "stuck", "trapped", "intruder", "weapon", "poison", "emergency",
]
MEDIUM_KEYWORDS = [
    "not working", "broken", "leak", "leaking", "no water", "no wifi",
    "slow", "smell", "infestation", "mosquito", "cockroach", "flicker",
]


def _rule_based(text: str):
    text = (text or "").lower()
    if any(k in text for k in HIGH_KEYWORDS):
        return "high", 0.6
    if any(k in text for k in MEDIUM_KEYWORDS):
        return "medium", 0.55
    return "low", 0.5


def _load_local_pipeline():
    global _pipeline, _pipeline_loaded
    if _pipeline_loaded:
        return _pipeline
    _pipeline_loaded = True
    if MODEL_PATH.exists():
        try:
            import joblib
            _pipeline = joblib.load(MODEL_PATH)
        except Exception:
            _pipeline = None
    return _pipeline


def _predict_local(text: str):
    pipeline = _load_local_pipeline()
    if pipeline is None:
        return _rule_based(text)
    try:
        proba = pipeline.predict_proba([text])[0]
        classes = pipeline.classes_
        best_idx = proba.argmax()
        return classes[best_idx], float(proba[best_idx])
    except Exception:
        return _rule_based(text)


def _predict_gemini(text: str, api_key: str, model_name: str):
    """
    Optional path: ask a real Gemini model to classify severity.
    Only used when settings.SEVERITY_ENGINE == "gemini" and a valid
    GEMINI_API_KEY is set. Requires `pip install google-generativeai`.
    """
    import google.generativeai as genai

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    prompt = (
        "Classify the severity of this hostel complaint as exactly one word: "
        "high, medium, or low. High = safety/health/security emergency. "
        "Medium = real inconvenience needing prompt attention. "
        "Low = minor request or cosmetic issue.\n\n"
        f"Complaint: {text}\n\nAnswer with one word only."
    )
    response = model.generate_content(prompt)
    answer = (response.text or "").strip().lower()
    for label in ("high", "medium", "low"):
        if label in answer:
            return label, 0.85
    raise ValueError(f"Unrecognized Gemini response: {answer!r}")


def predict_severity(text: str):
    from django.conf import settings

    if getattr(settings, "SEVERITY_ENGINE", "local") == "gemini" and getattr(settings, "GEMINI_API_KEY", ""):
        try:
            return _predict_gemini(text, settings.GEMINI_API_KEY, settings.GEMINI_MODEL)
        except Exception:
            pass  # fall through to local model

    return _predict_local(text)
