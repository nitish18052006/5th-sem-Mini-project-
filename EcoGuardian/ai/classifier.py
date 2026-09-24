import csv
import os

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATA_FILE = os.path.join(
    BASE_DIR,
    "training_data.csv"
)


def load_training_data():

    texts = []
    labels = []

    with open(
        DATA_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            text = row["text"].strip()
            category = row["category"].strip()

            texts.append(text)
            labels.append(category)

    return texts, labels


# Load training data
training_texts, training_labels = load_training_data()


# Convert text into numerical TF-IDF features
vectorizer = TfidfVectorizer(
    lowercase=True,
    stop_words="english",
    ngram_range=(1, 2)
)

X = vectorizer.fit_transform(
    training_texts
)


# Train Logistic Regression model
model = LogisticRegression(
    max_iter=1000
)

model.fit(
    X,
    training_labels
)


def get_severity(text):

    text = text.lower()

    high_words = [
        "toxic",
        "chemical",
        "poison",
        "fire",
        "dangerous",
        "hazardous",
        "contamination",
        "dead fish",
        "sewage",
        "smoke",
        "illegal dumping"
    ]

    medium_words = [
        "garbage",
        "waste",
        "plastic",
        "pollution",
        "noise",
        "dirty",
        "smell",
        "dust"
    ]

    for word in high_words:

        if word in text:
            return "High"

    for word in medium_words:

        if word in text:
            return "Medium"

    return "Low"


def calculate_priority(
    confidence,
    severity
):

    base_score = int(
        confidence * 70
    )

    severity_points = {
        "Low": 10,
        "Medium": 20,
        "High": 30
    }

    score = (
        base_score
        + severity_points.get(
            severity,
            10
        )
    )

    return min(
        100,
        max(0, score)
    )


def get_environmental_information(
    category
):

    information = {

        "Waste Management": {
            "impacts": [
                "Soil contamination",
                "Water pollution",
                "Spread of disease",
                "Bad odour"
            ],
            "solutions": [
                "Separate waste at source",
                "Recycle reusable materials",
                "Avoid open dumping",
                "Use proper waste collection systems"
            ]
        },

        "Plastic Pollution": {
            "impacts": [
                "Marine pollution",
                "Animal injuries",
                "Blocked drainage",
                "Microplastic contamination"
            ],
            "solutions": [
                "Avoid single-use plastic",
                "Use reusable bags",
                "Recycle plastic materials",
                "Dispose of plastic correctly"
            ]
        },

        "Water Pollution": {
            "impacts": [
                "Unsafe drinking water",
                "Damage to aquatic life",
                "Disease transmission",
                "Ecosystem damage"
            ],
            "solutions": [
                "Prevent dumping into water bodies",
                "Treat wastewater",
                "Reduce chemical discharge",
                "Keep water sources clean"
            ]
        },

        "Air Pollution": {
            "impacts": [
                "Respiratory problems",
                "Reduced air quality",
                "Damage to vegetation",
                "Climate impacts"
            ],
            "solutions": [
                "Reduce vehicle emissions",
                "Avoid burning waste",
                "Use public transport",
                "Increase green cover"
            ]
        },

        "Noise Pollution": {
            "impacts": [
                "Stress",
                "Sleep disturbance",
                "Hearing problems",
                "Effects on wildlife"
            ],
            "solutions": [
                "Reduce unnecessary honking",
                "Control loudspeakers",
                "Maintain vehicle silencers",
                "Follow noise regulations"
            ]
        },

        "Deforestation": {
            "impacts": [
                "Loss of biodiversity",
                "Soil erosion",
                "Habitat destruction",
                "Climate impacts"
            ],
            "solutions": [
                "Plant trees",
                "Protect existing forests",
                "Avoid unnecessary tree cutting",
                "Support forest conservation"
            ]
        },

        "Energy": {
            "impacts": [
                "Higher energy consumption",
                "Increased emissions",
                "Resource depletion",
                "Environmental degradation"
            ],
            "solutions": [
                "Switch off unused devices",
                "Use energy-efficient appliances",
                "Use renewable energy",
                "Reduce unnecessary electricity usage"
            ]
        }
    }

    return information.get(
        category,
        {
            "impacts": [
                "Possible environmental damage"
            ],
            "solutions": [
                "Follow responsible environmental practices"
            ]
        }
    )


def classify_environmental_issue(text):

    text = text.strip()

    if not text:

        return {
            "category": "Unknown",
            "confidence": 0,
            "severity": "Low",
            "priority_score": 0,
            "impacts": [],
            "solutions": []
        }

    transformed_text = vectorizer.transform(
        [text]
    )

    prediction = model.predict(
        transformed_text
    )[0]

    probabilities = model.predict_proba(
        transformed_text
    )[0]

    confidence = float(
        max(probabilities)
    )

    severity = get_severity(
        text
    )

    priority_score = calculate_priority(
        confidence,
        severity
    )

    information = get_environmental_information(
        prediction
    )

    return {
        "category": prediction,
        "confidence": round(
            confidence * 100,
            2
        ),
        "severity": severity,
        "priority_score": priority_score,
        "impacts": information["impacts"],
        "solutions": information["solutions"]
    }