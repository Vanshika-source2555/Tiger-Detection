from datetime import datetime
from server.config import ALERT_LOG_FILE

def create_alert(camera_id, confidence, image_path):
    message = (
        "\n===== TIGER ALERT =====\n"
        f"Camera ID: {camera_id}\n"
        f"Confidence: {confidence}%\n"
        f"Image Path: {image_path}\n"
        f"Time: {datetime.now()}\n"
        "=======================\n"
    )

    with open(ALERT_LOG_FILE, "a") as file:
        file.write(message)

    print(message)
    return message


def read_alerts():
    try:
        with open(ALERT_LOG_FILE, "r") as file:
            return file.read()
    except FileNotFoundError:
        return "No alerts found"