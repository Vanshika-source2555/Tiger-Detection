import os
import cv2
import joblib
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")

IMAGE_SIZE = (64, 64)

model = None

if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
    print("Model loaded successfully")
else:
    print("Model file not found:", MODEL_PATH)


def preprocess_image(image_path):
    image = cv2.imread(image_path)

    if image is None:
        return None

    image = cv2.resize(image, IMAGE_SIZE)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = image.flatten()
    image = image / 255.0
    image = image.reshape(1, -1)

    return image


def predict_image(image_path):
    if model is None:
        return "Model not trained", 0.0

    image = preprocess_image(image_path)

    if image is None:
        return "Invalid image", 0.0

    prediction = model.predict(image)[0]

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(image)[0]
        classes = list(model.classes_)

        if 1 in classes:
            tiger_index = classes.index(1)
            tiger_confidence = probabilities[tiger_index] * 100

            if tiger_confidence >= 10 or prediction == 1:
             return "Tiger", round(float(tiger_confidence), 2)

        non_tiger_confidence = max(probabilities) * 100
        return "Non-Tiger", round(float(non_tiger_confidence), 2)

    if prediction == 1 or str(prediction).lower() == "tiger":
        return "Tiger", 80.0

    return "Non-Tiger", 80.0