from flask import Flask, request, jsonify, Response
import os
import cv2
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas

from predict import predict_image

from database import (
    signup_user,
    login_user,
    change_password,
    save_detection,
    get_history,
    get_stats,
    get_user_stats
)

from server.config import (
    UPLOAD_FOLDER,
    SAVED_TIGER_FOLDER,
    CAPTURED_FRAMES_FOLDER,
    REPORT_FOLDER,
    GRAPH_FOLDER,
    PDF_FOLDER,
    TEMP_FRAMES_FOLDER
)

from server.camera_manager import (
    start_camera,
    stop_camera,
    get_camera_status,
    get_latest_frame
)

from server.health_service import get_server_health
from server.storage_service import delete_old_files
from server.alert_service import read_alerts

app = Flask(__name__)


@app.route("/")
def home():
    return "Advanced Tiger Detection Server Running"


def convert_camera_url(camera_url):
    if camera_url is None or camera_url.strip() == "":
        return 0

    camera_url = camera_url.strip()

    if camera_url.isdigit():
        return int(camera_url)

    return camera_url


def save_tiger_image(image_path):
    time_name = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    save_path = os.path.join(SAVED_TIGER_FOLDER, f"tiger_{time_name}.jpg")

    image = cv2.imread(image_path)

    if image is not None:
        cv2.imwrite(save_path, image)

    return save_path


def generate_frames(camera_id="CAM_1"):
    while True:
        frame = get_latest_frame(camera_id)

        if frame is None:
            frame = 255 * np.ones((480, 640, 3), dtype=np.uint8)
            cv2.putText(
                frame,
                f"Start {camera_id}",
                (180, 240),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2
            )

        ret, buffer = cv2.imencode(".jpg", frame)

        if not ret:
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + buffer.tobytes()
            + b"\r\n"
        )


@app.route("/video_feed")
def video_feed():
    return Response(
        generate_frames("CAM_1"),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/video_feed/<camera_id>")
def video_feed_camera(camera_id):
    return Response(
        generate_frames(camera_id),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/snapshot/<camera_id>")
def snapshot(camera_id):
    frame = get_latest_frame(camera_id)

    if frame is None:
        frame = 255 * np.ones((480, 640, 3), dtype=np.uint8)

        cv2.putText(
            frame,
            f"Start {camera_id}",
            (180, 240),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            2
        )

    ret, buffer = cv2.imencode(".jpg", frame)

    if not ret:
        return "Frame error"

    response = Response(buffer.tobytes(), mimetype="image/jpeg")
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response


@app.route("/start_camera", methods=["POST"])
def start_camera_route():
    camera_id = request.form.get("camera_id", "CAM_1")
    camera_url = convert_camera_url(request.form.get("camera_url", "0"))

    message = start_camera(camera_id, camera_url)

    return jsonify({
        "success": True,
        "message": message,
        "camera_id": camera_id
    })


@app.route("/stop_camera", methods=["POST"])
def stop_camera_route():
    camera_id = request.form.get("camera_id", "CAM_1")
    message = stop_camera(camera_id)

    return jsonify({
        "success": True,
        "message": message,
        "camera_id": camera_id
    })


@app.route("/start_multi_camera", methods=["POST"])
def start_multi_camera_route():
    cameras = {
        "CAM_1": request.form.get("cam1", "0"),
        "CAM_2": request.form.get("cam2", "videos/cam2.mp4"),
        "CAM_3": request.form.get("cam3", "videos/cam3.mp4"),
        "CAM_4": request.form.get("cam4", "videos/cam4.mp4")
    }

    messages = {}

    for camera_id, camera_url in cameras.items():
        messages[camera_id] = start_camera(
            camera_id,
            convert_camera_url(camera_url)
        )

    return jsonify({
        "success": True,
        "messages": messages
    })


@app.route("/stop_multi_camera", methods=["POST"])
def stop_multi_camera_route():
    messages = {}

    for camera_id in ["CAM_1", "CAM_2", "CAM_3", "CAM_4"]:
        messages[camera_id] = stop_camera(camera_id)

    return jsonify({
        "success": True,
        "messages": messages
    })


@app.route("/camera_status", methods=["GET"])
def camera_status_route():
    return jsonify(get_camera_status())


@app.route("/server_health", methods=["GET"])
def server_health_route():
    return jsonify(get_server_health())


@app.route("/cleanup_storage", methods=["GET"])
def cleanup_storage_route():
    result1 = delete_old_files(TEMP_FRAMES_FOLDER, hours=24)
    result2 = delete_old_files(CAPTURED_FRAMES_FOLDER, hours=24)
    result3 = delete_old_files(UPLOAD_FOLDER, hours=24)

    return jsonify({
        "success": True,
        "temp_frames": result1,
        "captured_frames": result2,
        "uploads": result3
    })


@app.route("/alerts", methods=["GET"])
def alerts_route():
    return read_alerts()


@app.route("/clear_alerts", methods=["POST"])
def clear_alerts_route():
    with open("alerts_log.txt", "w") as file:
        file.write("")

    return "Alerts cleared successfully"


@app.route("/api", methods=["POST"])
def api():
    action = request.form.get("action")

    if action == "signup":
        email = request.form.get("email")
        password = request.form.get("password")
        return signup_user(email, password)

    elif action == "login":
        email = request.form.get("email")
        password = request.form.get("password")
        return login_user(email, password)

    elif action == "change_password":
        email = request.form.get("email")
        password_data = request.form.get("password")

        old_password, new_password = password_data.split(",")

        return change_password(email, old_password, new_password)

    elif action == "detect_photo":
        if "file" not in request.files:
            return jsonify({
                "success": False,
                "message": "No image file received"
            })

        file = request.files["file"]

        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        result, confidence = predict_image(file_path)

        saved_path = ""
        notification = "No Tiger Detected"

        if result == "Tiger":
            saved_path = save_tiger_image(file_path)
            notification = "Tiger Detected in Photo"

        save_detection(
            username="admin",
            source_type="Photo",
            file_name=file.filename,
            result=result,
            confidence=confidence,
            image_path=saved_path
        )

        return jsonify({
            "success": True,
            "type": "photo",
            "notification": notification,
            "result": result,
            "confidence": confidence,
            "uploaded_file": file_path,
            "saved_image": saved_path
        })

    elif action == "detect_video":
        if "file" not in request.files:
            return jsonify({
                "success": False,
                "message": "No video file received"
            })

        file = request.files["file"]

        video_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(video_path)

        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            return jsonify({
                "success": False,
                "message": "Video could not be opened"
            })

        frame_count = 0
        checked_frames = 0
        tiger_frames = 0
        nontiger_frames = 0
        best_confidence = 0
        best_frame_path = ""

        while True:
            success, frame = cap.read()

            if not success:
                break

            frame_count += 1

            if frame_count % 30 == 0:
                checked_frames += 1

                frame_name = "frame_" + str(checked_frames) + ".jpg"
                frame_path = os.path.join(CAPTURED_FRAMES_FOLDER, frame_name)

                cv2.imwrite(frame_path, frame)

                result, confidence = predict_image(frame_path)

                if result == "Tiger":
                    tiger_frames += 1

                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_frame_path = save_tiger_image(frame_path)
                else:
                    nontiger_frames += 1

        cap.release()

        final_result = "Tiger Detected" if tiger_frames > 0 else "No Tiger Detected"

        text_report_path = create_video_report(
            final_result,
            checked_frames,
            tiger_frames,
            nontiger_frames,
            best_confidence
        )

        graph_path = create_video_graph(tiger_frames, nontiger_frames)

        pdf_path = create_pdf_report(
            final_result,
            checked_frames,
            tiger_frames,
            nontiger_frames,
            best_confidence,
            graph_path
        )

        save_detection(
            username="admin",
            source_type="Video",
            file_name=file.filename,
            result=final_result,
            confidence=best_confidence,
            image_path=pdf_path
        )

        return jsonify({
            "success": True,
            "type": "video",
            "notification": final_result,
            "result": final_result,
            "frames_checked": checked_frames,
            "tiger_frames": tiger_frames,
            "nontiger_frames": nontiger_frames,
            "confidence": best_confidence,
            "best_frame": best_frame_path,
            "text_report": text_report_path,
            "graph": graph_path,
            "pdf_report": pdf_path,
            "uploaded_video": video_path
        })

    elif action == "live_camera":
        return jsonify({
            "success": True,
            "message": "Use /start_camera and /snapshot/CAM_1 for live camera preview"
        })

    elif action == "history":
        return get_history()

    elif action == "stats":
        return get_stats()

    elif action == "user_stats":
        username = request.form.get("username")
        return get_user_stats(username)

    elif action == "start_cctv_server":
        camera_id = request.form.get("camera_id", "CAM_1")
        camera_url = convert_camera_url(request.form.get("camera_url", "0"))
        message = start_camera(camera_id, camera_url)

        return jsonify({
            "success": True,
            "message": message
        })

    elif action == "stop_cctv_server":
        camera_id = request.form.get("camera_id", "CAM_1")
        message = stop_camera(camera_id)

        return jsonify({
            "success": True,
            "message": message
        })

    elif action == "camera_status":
        return jsonify(get_camera_status())

    elif action == "server_health":
        return jsonify(get_server_health())

    elif action == "cleanup_storage":
        result1 = delete_old_files(TEMP_FRAMES_FOLDER, hours=24)
        result2 = delete_old_files(CAPTURED_FRAMES_FOLDER, hours=24)
        result3 = delete_old_files(UPLOAD_FOLDER, hours=24)

        return jsonify({
            "success": True,
            "temp_frames": result1,
            "captured_frames": result2,
            "uploads": result3
        })

    elif action == "alerts":
        return read_alerts()

    else:
        return jsonify({
            "success": False,
            "message": "Invalid action"
        })


def create_video_report(
    final_result,
    checked_frames,
    tiger_frames,
    nontiger_frames,
    best_confidence
):
    time_name = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(REPORT_FOLDER, "report_" + time_name + ".txt")

    with open(report_path, "w") as f:
        f.write("Tiger Detection Video Report\n")
        f.write("----------------------------\n")
        f.write("Date Time: " + time_name + "\n")
        f.write("Result: " + final_result + "\n")
        f.write("Frames Checked: " + str(checked_frames) + "\n")
        f.write("Tiger Frames: " + str(tiger_frames) + "\n")
        f.write("NonTiger Frames: " + str(nontiger_frames) + "\n")
        f.write("Saved Tiger Screenshots: " + str(tiger_frames) + "\n")
        f.write("Best Confidence: " + str(best_confidence) + "%\n")

    with open("report.txt", "w") as f:
        f.write("Latest Text Report: " + report_path)

    return report_path


def create_video_graph(tiger_frames, nontiger_frames):
    graph_path = os.path.join(GRAPH_FOLDER, "video_result_graph.png")

    labels = ["Tiger Frames", "NonTiger Frames"]
    values = [tiger_frames, nontiger_frames]

    plt.figure()
    plt.bar(labels, values)
    plt.title("Video Detection Result")
    plt.ylabel("Number of Frames")
    plt.savefig(graph_path)
    plt.close()

    return graph_path


def create_pdf_report(
    final_result,
    checked_frames,
    tiger_frames,
    nontiger_frames,
    best_confidence,
    graph_path
):
    time_name = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_path = os.path.join(PDF_FOLDER, "report_" + time_name + ".pdf")

    c = canvas.Canvas(pdf_path)

    c.setFont("Helvetica-Bold", 18)
    c.drawString(100, 780, "Tiger Detection Report")

    c.setFont("Helvetica", 12)
    c.drawString(100, 730, "Date Time: " + time_name)
    c.drawString(100, 700, "Result: " + final_result)
    c.drawString(100, 670, "Frames Checked: " + str(checked_frames))
    c.drawString(100, 640, "Tiger Frames: " + str(tiger_frames))
    c.drawString(100, 610, "NonTiger Frames: " + str(nontiger_frames))
    c.drawString(100, 580, "Saved Tiger Screenshots: " + str(tiger_frames))
    c.drawString(100, 550, "Best Confidence: " + str(best_confidence) + "%")

    if os.path.exists(graph_path):
        c.drawImage(graph_path, 100, 300, width=350, height=220)

    c.save()

    return pdf_path


if __name__ == "__main__":
   app.run(host="127.0.0.1", port=5000, debug=False, threaded=True, use_reloader=False)