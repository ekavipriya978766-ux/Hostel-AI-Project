"""
Trains the local, offline severity-prediction model used by
`complaints.ml.severity_predictor`.

This is a small TF-IDF + Logistic Regression text classifier trained on a
hand-labeled synthetic dataset of hostel complaints. It requires no
internet access and no API key, so the project runs end-to-end out of the
box. Run again any time you want to retrain after editing TRAINING_DATA:

    python manage.py train_severity_model
"""

import json
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

MODEL_DIR = Path(__file__).resolve().parent
MODEL_PATH = MODEL_DIR / "severity_model.joblib"

# label: high / medium / low
TRAINING_DATA = [
    # ---- HIGH: safety, health, security, fire, structural risk ----
    ("There is a live wire hanging near my bed and I got a mild shock touching it", "high"),
    ("Short circuit in the room, sparks are coming out of the socket, very dangerous", "high"),
    ("I smell gas leak near the kitchen, please send someone immediately", "high"),
    ("A stranger entered the hostel at night and tried to open my room door", "high"),
    ("My roommate is very sick with high fever and vomiting, needs urgent medical help", "high"),
    ("Someone stole my laptop and phone from the room last night", "high"),
    ("The ceiling fan fell down while running, almost hit me", "high"),
    ("There was a small fire in the mess kitchen area, everyone panicked", "high"),
    ("The bathroom door lock is broken and anyone can walk in, feels unsafe especially at night", "high"),
    ("I am being harassed by a senior student repeatedly, I feel unsafe", "high"),
    ("Water is leaking directly onto the electrical switchboard in my room", "high"),
    ("The staircase railing is broken and someone almost fell down the stairs", "high"),
    ("Food from the mess caused severe food poisoning, many students are vomiting", "high"),
    ("No security guard at the gate at night, anyone can enter the hostel", "high"),
    ("Smoke is coming out of the wiring behind my study table", "high"),
    ("There is a gas cylinder leaking near the common kitchen, urgent", "high"),
    ("My window grill is broken and it's on the ground floor, unsafe at night", "high"),
    ("I found a snake near the hostel entrance, everyone is scared", "high"),
    ("The elevator got stuck with three students inside for 20 minutes", "high"),
    ("There was a physical fight between students in the corridor, someone got hurt", "high"),

    # ---- MEDIUM: real inconvenience, not an emergency ----
    ("The water heater in my bathroom is not working since two days", "medium"),
    ("There is no wifi in my room since yesterday, I have online classes", "medium"),
    ("The tap in my bathroom is leaking continuously and wasting water", "medium"),
    ("Food quality in the mess has been really bad for the past week", "medium"),
    ("My room light keeps flickering, the tube light needs replacement", "medium"),
    ("The washing machine on my floor is not working", "medium"),
    ("There is a bad smell coming from the drainage near my room", "medium"),
    ("My cupboard door is broken and doesn't close properly", "medium"),
    ("The room has not been cleaned by housekeeping for a week", "medium"),
    ("Mosquitoes are a big problem in my room, no nets provided", "medium"),
    ("The geyser takes too long to heat water in the morning", "medium"),
    ("Internet speed is extremely slow on the entire floor", "medium"),
    ("My chair is broken and wobbles when I sit on it", "medium"),
    ("The corridor lights are not working at night on my floor", "medium"),
    ("Cold water only, no hot water available in common bathroom", "medium"),
    ("There is a cockroach infestation in the common bathroom", "medium"),
    ("The mess food is repeated every day, please change the menu", "medium"),
    ("Door of my room does not lock properly", "medium"),
    ("The dustbin near my room has not been emptied in days", "medium"),
    ("Fan speed regulator in my room is not working", "medium"),

    # ---- LOW: minor requests, cosmetic issues ----
    ("Can I get an extra blanket for my room please", "low"),
    ("The paint on my wall is a bit faded, would like it repainted sometime", "low"),
    ("Requesting a spare key for my cupboard", "low"),
    ("Can housekeeping bring a new dustbin for my room", "low"),
    ("I would like the mess timing to be extended by 15 minutes", "low"),
    ("Requesting an extra chair for my room", "low"),
    ("The noticeboard near my room needs new pins", "low"),
    ("Can we get better quality tissue paper in the washroom", "low"),
    ("I would like to request a change of curtains in my room", "low"),
    ("Please add a mirror in the common bathroom", "low"),
    ("Requesting a small table lamp for my study table", "low"),
    ("Can the garden near the hostel be maintained a bit better", "low"),
    ("Would like an extra hook installed behind my door", "low"),
    ("Suggestion: please add a water purifier on the ground floor", "low"),
    ("The name plate outside my room fell off, please fix whenever possible", "low"),
    ("Requesting new bedsheets during the next laundry cycle", "low"),
    ("Can we get a suggestion box installed in the common room", "low"),
    ("Would appreciate a new mat outside the room", "low"),
    ("Please consider adding more plants in the hostel lobby", "low"),
    ("Requesting a minor repaint of the room door", "low"),
]


def train_and_save():
    texts = [t for t, _ in TRAINING_DATA]
    labels = [l for _, l in TRAINING_DATA]

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1, stop_words="english")),
        ("clf", LogisticRegression(max_iter=1000, class_weight="balanced")),
    ])
    pipeline.fit(texts, labels)

    import joblib
    joblib.dump(pipeline, MODEL_PATH)

    meta = {
        "n_samples": len(texts),
        "classes": sorted(set(labels)),
    }
    with open(MODEL_DIR / "severity_model_meta.json", "w") as f:
        json.dump(meta, f, indent=2)

    print(f"Trained severity model on {len(texts)} samples -> {MODEL_PATH}")
    return pipeline


if __name__ == "__main__":
    train_and_save()
