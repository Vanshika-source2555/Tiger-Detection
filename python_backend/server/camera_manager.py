import cv2
import os
import time
import threading
from datetime import datetime

from server.config import (
    TEMP_FRAMES_FOLDER,
    SAVED_TIGER_FOLDER,
    CAPTURED_FRAMES_FOLDER,
    FRAME_INTERVAL_SECONDS
)

from server.detector_service import detect_tiger
from server.alert_service import create_alert
from database import save_detection

camera_threads = {}
camera_status = {}
latest_frames = {}

TIGER_CONFIDENCE_THRESHOLD = 30
ALERT_COOLDOWN_SECONDS = 10


def save_frame(frame, folder, camera_id):
    os.makedirs(folder, exist_ok=True)
    file_name = f"{camera_id}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.jpg"
    file_path = os.path.join(folder, file_name)
    cv2.imwrite(file_path, frame)
    return file_path


def open_camera(camera_url):
    camera_url = str(camera_url).strip()

    if camera_url.isdigit():
        return cv2.VideoCapture(int(camera_url), cv2.CAP_DSHOW)

    if os.path.exists(camera_url):
        return cv2.VideoCapture(camera_url)

    return cv2.VideoCapture(camera_url)


def camera_worker(camera_id, camera_url):
    camera_status[camera_id] = {
        "status": "Starting",
        "source": str(camera_url),
        "last_result": "None",
        "last_confidence": 0,
        "frames_checked": 0,
        "tiger_count": 0,
        "last_alert_time": "No alert yet"
    }

    cap = open_camera(camera_url)

    if not cap.isOpened():
        camera_status[camera_id]["status"] = "Offline"
        print(camera_id, "camera could not open:", camera_url)
        return

    camera_status[camera_id]["status"] = "Online"

    last_processed_time = 0
    last_alert_time = 0
    checked_frames = 0
    tiger_frames = 0
    best_confidence = 0

    while camera_status[camera_id]["status"] == "Online":
        success, frame = cap.read()

        if not success:
            if isinstance(camera_url, str) and os.path.exists(camera_url):
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                success, frame = cap.read()

            if not success:
                camera_status[camera_id]["status"] = "Disconnected"
                print(camera_id, "disconnected")
                break

        latest_frames[camera_id] = frame.copy()
        current_time = time.time()

        if current_time - last_processed_time >= FRAME_INTERVAL_SECONDS:
            last_processed_time = current_time

            frame_path = save_frame(frame, TEMP_FRAMES_FOLDER, camera_id)
            captured_path = save_frame(frame, CAPTURED_FRAMES_FOLDER, camera_id)

            checked_frames += 1
            camera_status[camera_id]["frames_checked"] = checked_frames

            print("FRAME SAVED:", camera_id, captured_path)

            try:
                prediction = detect_tiger(captured_path)

                print("PREDICTION =", prediction)

                result = prediction["result"]
                confidence = float(prediction["confidence"])

                print("RESULT =", result)
                print("CONFIDENCE =", confidence)

            except Exception as e:
                print("DETECTION ERROR:", camera_id, e)

                prediction = {
                    "result": "Error",
                    "confidence": 0,
                    "is_tiger": False
                }

                result = "Error"
                confidence = 0

            if confidence > best_confidence:
                best_confidence = confidence

            if result == "Tiger":
                tiger_frames += 1

            camera_status[camera_id]["last_confidence"] = best_confidence
            camera_status[camera_id]["tiger_count"] = tiger_frames

            if tiger_frames > 0:
                camera_status[camera_id]["last_result"] = "Tiger"
            else:
                camera_status[camera_id]["last_result"] = "Non-Tiger"

            print(
                camera_id,
                "Dashboard Result:",
                camera_status[camera_id]["last_result"],
                "Best Confidence:",
                best_confidence,
                "Frames:",
                checked_frames,
                "Tiger Frames:",
                tiger_frames
            )

            if result == "Tiger":
                if current_time - last_alert_time >= ALERT_COOLDOWN_SECONDS:
                    last_alert_time = current_time
                    camera_status[camera_id]["last_alert_time"] = str(datetime.now())

                    saved_path = save_frame(frame, SAVED_TIGER_FOLDER, camera_id)

                    create_alert(
                        camera_id=camera_id,
                        confidence=confidence,
                        image_path=saved_path
                    )

                    save_detection(
                        username="admin",
                        source_type="Live Camera",
                        file_name=camera_id,
                        result="Tiger",
                        confidence=confidence,
                        image_path=saved_path
                    )

    cap.release()
    camera_status[camera_id]["status"] = "Stopped"


def start_camera(camera_id, camera_url):
    if camera_id in camera_status:
        camera_status[camera_id]["status"] = "Stopped"
        time.sleep(1)

    thread = threading.Thread(
        target=camera_worker,
        args=(camera_id, camera_url),
        daemon=True
    )

    camera_threads[camera_id] = thread
    thread.start()

    return f"{camera_id} started with source {camera_url}"


def stop_camera(camera_id):
    if camera_id not in camera_status:
        return f"{camera_id} not found"

    camera_status[camera_id]["status"] = "Stopped"

    if camera_id in latest_frames:
        del latest_frames[camera_id]

    return f"{camera_id} stopped successfully"


def get_camera_status():
    return camera_status


def get_latest_frame(camera_id="CAM_1"):
    return latest_frames.get(camera_id)