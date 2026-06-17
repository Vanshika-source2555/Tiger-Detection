import os
import cv2
import joblib
import numpy as np
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

TRAIN_PATH = "dataset/train"
VALIDATION_PATH = "dataset/validation"
TEST_PATH = "dataset/test"

MODEL_NAME = "model.pkl"


def get_label(folder_name):
    name = folder_name.lower().strip()

    if name == "tiger":
        return 1

    if name in ["nontiger", "non_tiger", "non tiger", "non-tiger"]:
        return 0

    return None


def read_images(folder_path):
    X = []
    y = []

    if not os.path.exists(folder_path):
        print("Folder not found:", folder_path)
        return np.array(X), np.array(y)

    for folder_name in os.listdir(folder_path):
        class_folder = os.path.join(folder_path, folder_name)

        if not os.path.isdir(class_folder):
            continue

        label = get_label(folder_name)

        if label is None:
            print("Skipping unknown folder:", folder_name)
            continue

        for file_name in os.listdir(class_folder):
            image_path = os.path.join(class_folder, file_name)

            if os.path.isdir(image_path):
                continue

            image = cv2.imread(image_path)

            if image is None:
                continue

            image = cv2.resize(image, (64, 64))
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            image = image.flatten()
            image = image / 255.0

            X.append(image)
            y.append(label)

    return np.array(X), np.array(y)


def check_accuracy(model, X, y, name):
    if len(X) == 0:
        print(name, "dataset is empty.")
        return 0

    if len(set(y)) < 2:
        print(name, "dataset has only one class. Accuracy skipped.")
        return 0

    prediction = model.predict(X)
    accuracy = accuracy_score(y, prediction) * 100

    print(name, "Accuracy:", round(accuracy, 2), "%")
    return accuracy


def make_graph(train_acc, val_acc, test_acc):
    os.makedirs("graphs", exist_ok=True)

    names = ["Train", "Validation", "Test"]
    values = [train_acc, val_acc, test_acc]

    plt.figure()
    plt.bar(names, values)
    plt.ylim(0, 100)
    plt.title("Tiger Detection Accuracy")
    plt.ylabel("Accuracy %")
    plt.savefig("graphs/accuracy_graph.png")
    plt.close()


print("Loading training dataset...")
X_train, y_train = read_images(TRAIN_PATH)

print("Loading validation dataset...")
X_val, y_val = read_images(VALIDATION_PATH)

print("Loading test dataset...")
X_test, y_test = read_images(TEST_PATH)

print("Training images:", len(X_train))
print("Validation images:", len(X_val))
print("Test images:", len(X_test))

print("Training classes found:", set(y_train))
print("Validation classes found:", set(y_val))
print("Test classes found:", set(y_test))

if len(X_train) == 0:
    print("No training images found.")
    exit()

if len(set(y_train)) < 2:
    print("ERROR: Training folder must have both classes.")
    print("Required folder structure:")
    print("dataset/train/Tiger")
    print("dataset/train/NonTiger")
    exit()

print("Training model... Please wait.")

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

train_acc = check_accuracy(model, X_train, y_train, "Training")
val_acc = check_accuracy(model, X_val, y_val, "Validation")
test_acc = check_accuracy(model, X_test, y_test, "Test")

joblib.dump(model, MODEL_NAME)

print("Model saved as:", MODEL_NAME)

make_graph(train_acc, val_acc, test_acc)

print("Graph saved in graphs folder.")
print("Training completed successfully.")