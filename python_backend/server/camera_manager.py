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


def detect_tiger_full_frame(frame, camera_id):
    frame_path = save_frame(frame, TEMP_FRAMES_FOLDER, camera_id + "_full")
    prediction = detect_tiger(frame_path)

    print("Full Frame Prediction:", prediction)

    if prediction["result"] == "Tiger":
        return "Tiger"

    return "No Tiger Detected"


def detect_tiger_multi_crop(frame, camera_id):
    h, w, _ = frame.shape

    crops = [
        frame,                                      # full frame
        frame[h // 4: 3 * h // 4, w // 4: 3 * w // 4],  # center
        frame[h // 4: 3 * h // 4, 0: w // 2],      # left
        frame[h // 4: 3 * h // 4, w // 2: w],      # right
        frame[h // 2: h, 0: w // 2],               # bottom left
        frame[h // 2: h, w // 2: w],               # bottom right
        frame[0: h // 2, 0: w // 2],               # top left
        frame[0: h // 2, w // 2: w]                # top right
    ]

    for i, crop in enumerate(crops):
        if crop is None or crop.size == 0:
            continue

        crop_path = save_frame(
            crop,
            TEMP_FRAMES_FOLDER,
            camera_id + "_crop_" + str(i)
        )

        prediction = detect_tiger(crop_path)

        print("Crop", i, "Prediction:", prediction)

        if prediction["result"] == "Tiger":
            return "Tiger"

    return "No Tiger Detected"


def final_tiger_detection(frame, camera_id):
    # Step 1: check full frame
    full_result = detect_tiger_full_frame(frame, camera_id)

    if full_result == "Tiger":
        return "Tiger"

    # Step 2: if full frame fails, check crops
    crop_result = detect_tiger_multi_crop(frame, camera_id)

    if crop_result == "Tiger":
        return "Tiger"

    return "No Tiger Detected"


def camera_worker(camera_id, camera_url):
    camera_status[camera_id] = {
        "status": "Starting",
        "source": str(camera_url),
        "last_result": "None",
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
    tiger_count = 0

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

            captured_path = save_frame(frame, CAPTURED_FRAMES_FOLDER, camera_id)

            checked_frames += 1
            camera_status[camera_id]["frames_checked"] = checked_frames

            print("Frame checked:", camera_id, captured_path)

            try:
                result = final_tiger_detection(frame, camera_id)
                print("Final Result:", camera_id, result)

            except Exception as e:
                print("Detection error:", camera_id, e)
                result = "Error"

            if result == "Tiger":
                camera_status[camera_id]["last_result"] = "Tiger"

                if current_time - last_alert_time >= ALERT_COOLDOWN_SECONDS:
                    last_alert_time = current_time
                    tiger_count += 1

                    camera_status[camera_id]["tiger_count"] = tiger_count
                    camera_status[camera_id]["last_alert_time"] = str(datetime.now())

                    saved_path = save_frame(frame, SAVED_TIGER_FOLDER, camera_id)

                    create_alert(
                        camera_id=camera_id,
                        confidence=0,
                        image_path=saved_path
                    )

                    save_detection(
                        username="admin",
                        source_type="Live Camera",
                        file_name=camera_id,
                        result="Tiger Detected",
                        confidence=0,
                        image_path=saved_path
                    )

                    print(camera_id, "Tiger Detected - Sighting Saved")

            elif result == "No Tiger Detected":
                camera_status[camera_id]["last_result"] = "No Tiger Detected"

            else:
                camera_status[camera_id]["last_result"] = result

            print(
                camera_id,
                "Status:",
                camera_status[camera_id]["last_result"],
                "Frames:",
                checked_frames,
                "Tiger Count:",
                tiger_count
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

    return f"{camera_id} started"


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