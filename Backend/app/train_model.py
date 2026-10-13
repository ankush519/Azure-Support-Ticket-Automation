import csv
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "sample_data" / "tickets.csv"
MODEL_PATH = BASE_DIR / "app" / "ticket_model.joblib"

# 1. Load labelled examples
with open(DATA_PATH, "r", encoding="utf-8", newline="") as file:
    rows = list(csv.DictReader(file))

messages = [row["message"] for row in rows]
labels = [row["category"] for row in rows]

# 2. Split BEFORE fitting or tuning
X_train, X_test, y_train, y_test = train_test_split(
    messages,
    labels,
    test_size=10,
    random_state=42,
    stratify=labels,
)

print("Training examples:", len(X_train))
print("Testing examples:", len(X_test))

# Keep the original 10 test tickets separate.
test_ids = {3, 7, 8, 13, 15, 18, 20, 21, 27, 29}

train_rows = [
    row for row in rows
    if int(row["ticket_id"]) not in test_ids
]

test_rows = [
    row for row in rows
    if int(row["ticket_id"]) in test_ids
]

X_train = [row["message"] for row in train_rows]
y_train = [row["category"] for row in train_rows]

X_test = [row["message"] for row in test_rows]
y_test = [row["category"] for row in test_rows]

print("Training examples:", len(X_train))
print("Testing examples:", len(X_test))


# 3. Build the ML pipeline
model = Pipeline([
    ("tfidf", TfidfVectorizer(ngram_range=(1, 2))),
    ("classifier", LogisticRegression(max_iter=1000)),
])

# 4. Train only on the training examples
model.fit(X_train, y_train)

# 5. Evaluate on the held-out test set
predictions = model.predict(X_test)

print("\nTest accuracy:", accuracy_score(y_test, predictions))
print("\nClassification report:")
print(classification_report(
    y_test,
    predictions,
    zero_division=0,
))

print("\nTest predictions:")
for message, actual, predicted in zip(
    X_test, y_test, predictions
):
    print(
        f"Message: {message}\n"
        f"Actual: {actual} | Predicted: {predicted}\n"
    )

# 6. Save the fitted pipeline
joblib.dump(model, MODEL_PATH)
print("Model saved to:", MODEL_PATH)