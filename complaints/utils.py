"""
Smart complaint processing helpers.

`detect_department` implements requirement 3 ("Internal department detection
- hidden from UI"): a fast, deterministic keyword classifier that decides
which internal team a complaint belongs to. It never touches the student
facing templates - only management/warden/admin views and the assigned
warden's `department` field ever see it.
"""

DEPARTMENT_KEYWORDS = {
    "Electrical": [
        "electric", "wiring", "socket", "switch", "fan", "light", "bulb",
        "power cut", "short circuit", "mcb", "voltage", "current",
    ],
    "Plumbing": [
        "water", "tap", "leak", "leakage", "pipe", "drain", "toilet",
        "bathroom", "flush", "sewage", "washroom", "geyser", "shower",
    ],
    "Food & Mess": [
        "food", "mess", "meal", "canteen", "dining", "breakfast", "lunch",
        "dinner", "hygiene", "cook", "kitchen", "menu", "stale",
    ],
    "Cleanliness": [
        "dirty", "clean", "garbage", "trash", "dust", "smell", "insect",
        "cockroach", "mosquito", "housekeeping", "sweep",
    ],
    "Security": [
        "theft", "stolen", "security", "guard", "unsafe", "unknown person",
        "lock", "cctv", "intruder", "harassment", "safety",
    ],
    "Internet & Wi-Fi": [
        "wifi", "wi-fi", "internet", "network", "router", "connectivity",
        "broadband", "lan",
    ],
    "Furniture": [
        "bed", "chair", "table", "cupboard", "mattress", "furniture",
        "broken", "door", "window", "lock broken", "wardrobe",
    ],
}

DEFAULT_DEPARTMENT = "General"


def detect_department(text: str) -> str:
    """Keyword-score the complaint text and return the best-matching
    internal department, defaulting to 'General' when nothing matches."""
    text = (text or "").lower()
    scores = {}
    for department, keywords in DEPARTMENT_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        if score:
            scores[department] = score
    if not scores:
        return DEFAULT_DEPARTMENT
    return max(scores, key=scores.get)
