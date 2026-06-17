import os

BASE_DIR = os.getcwd()

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
SAVED_TIGER_FOLDER = os.path.join(BASE_DIR, "saved_tigers")
CAPTURED_FRAMES_FOLDER = os.path.join(BASE_DIR, "captured_frames")
TEMP_FRAMES_FOLDER = os.path.join(BASE_DIR, "temp_frames")
REPORT_FOLDER = os.path.join(BASE_DIR, "reports")
GRAPH_FOLDER = os.path.join(BASE_DIR, "graphs")
PDF_FOLDER = os.path.join(BASE_DIR, "pdf_reports")
ALERT_LOG_FILE = os.path.join(BASE_DIR, "alerts_log.txt")

FRAME_INTERVAL_SECONDS = 1
CONFIDENCE_THRESHOLD = 70

for folder in [
    UPLOAD_FOLDER,
    SAVED_TIGER_FOLDER,
    CAPTURED_FRAMES_FOLDER,
    TEMP_FRAMES_FOLDER,
    REPORT_FOLDER,
    GRAPH_FOLDER,
    PDF_FOLDER
]:
    os.makedirs(folder, exist_ok=True)