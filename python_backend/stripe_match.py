import cv2
import os
import pickle
from datetime import datetime

DATABASE_FILE = "stripe_database.pkl"

orb = cv2.ORB_create(nfeatures=1500)


def extract_features(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    if image is None:
        return None

    image = cv2.resize(image, (300, 300))
    image = cv2.equalizeHist(image)

    _, descriptors = orb.detectAndCompute(image, None)
    return descriptors


def load_database():
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, "rb") as f:
            return pickle.load(f)

    return []


def save_database(database):
    with open(DATABASE_FILE, "wb") as f:
        pickle.dump(database, f)


def identify_tiger(image_path):
    database = load_database()
    test_descriptors = extract_features(image_path)

    if test_descriptors is None:
        return "New Tiger Recorded"

    matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    best_match_count = 0

    for tiger in database:
        stored_descriptors = tiger.get("descriptors")

        if stored_descriptors is None:
            continue

        matches = matcher.match(test_descriptors, stored_descriptors)
        good_matches = [m for m in matches if m.distance < 55]

        if len(good_matches) > best_match_count:
            best_match_count = len(good_matches)

    if best_match_count >= 35:
        return "Same Tiger Seen Again"

    database.append({
        "image": os.path.basename(image_path),
        "descriptors": test_descriptors,
        "time": str(datetime.now())
    })

    save_database(database)

    return "New Tiger Recorded"


def save_new_stripe(image_path):
    """
    Compatibility function for app.py.
    It saves a new tiger stripe record if not already matched.
    """
    return identify_tiger(image_path)