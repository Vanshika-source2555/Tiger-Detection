import os
import re
import openpyxl
from dotenv import load_dotenv
import google.generativeai as genai

# Load .env file
load_dotenv()

QA_FILE = "qa_dataset.xlsx"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    print("Gemini API key loaded")
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("Gemini API key NOT loaded")

gemini_model = genai.GenerativeModel("gemini-2.0-flash-lite")


def clean_text(text):
    text = str(text).lower()
    text = re.sub(r"[^a-z0-9\s_.]", " ", text)
    return text.strip()


def load_qa_dataset():
    data = []

    if not os.path.exists(QA_FILE):
        return data

    wb = openpyxl.load_workbook(QA_FILE, data_only=True)
    sheet = wb.active

    for row in sheet.iter_rows(min_row=3, values_only=True):
        if len(row) < 6:
            continue

        question = row[4]
        answer = row[5]

        if question and answer:
            data.append({
                "question": str(question),
                "answer": str(answer),
                "clean_question": clean_text(question)
            })

    return data


def dataset_answer(user_question):
    q = clean_text(user_question)
    words = set(q.split())

    best_score = 0
    best_answer = None

    for item in load_qa_dataset():
        dataset_words = set(item["clean_question"].split())
        score = len(words.intersection(dataset_words))

        if item["clean_question"] == q:
            score += 30

        if q in item["clean_question"]:
            score += 15

        if score > best_score:
            best_score = score
            best_answer = item["answer"]

    if best_score >= 2:
        return best_answer

    return None


def gemini_answer(question):
    if not GEMINI_API_KEY:
        return None

    try:
        prompt = f"""
You are Tiger AI Assistant.

Give short, simple, and impactful answers.

Focus only on:
image detection, video detection, live camera, same tiger identification,
alerts, history, reports, dataset, model training, backend, Java frontend,
and troubleshooting.

Give practical suggestions.
Final real-world action must be done by the user.

Question:
{question}
"""

        response = gemini_model.generate_content(prompt)
        return response.text

    except Exception as e:
        print("Gemini chat error:", e)
        return None


def fallback_answer(question):
    q = question.lower()

    if "camera" in q:
        return "Camera monitoring checks live frames.\n\nSuggestion:\nCheck camera source and live preview."

    if "tiger" in q:
        return "Tiger detection checks images, videos, and camera frames.\n\nSuggestion:\nReview saved image and history."

    if "error" in q or "problem" in q:
        return "Problem detected.\n\nSuggestion:\nCheck Flask backend, model.pkl, camera source, and terminal logs."

    return (
        "I can help with image detection, video detection, live camera, "
        "same tiger identification, alerts, history, reports, dataset, "
        "model training, backend, Java frontend, and troubleshooting."
    )


def ai_chat_answer(question):
    answer = dataset_answer(question)

    if answer:
        return answer

    answer = gemini_answer(question)

    if answer:
        return answer

    return fallback_answer(question)


def local_camera_ai_summary(camera_id, status, result, frames, same_tiger=""):
    r = (result or "").lower()
    s = (status or "").lower()

    if "tiger" in r and "no tiger" not in r:
        return (
            "AI Summary:\n"
            f"Tiger activity detected on {camera_id}.\n\n"
            "AI Suggestion:\n"
            "Review saved image and check nearby cameras.\n\n"
            "AI Decision Support:\n"
            "Important detection. User should verify and continue monitoring."
        )

    if "no tiger" in r:
        return (
            "AI Summary:\n"
            f"No tiger activity detected on {camera_id}.\n\n"
            "AI Suggestion:\n"
            "Continue monitoring.\n\n"
            "AI Decision Support:\n"
            "No immediate action required."
        )

    if "offline" in r or "disconnect" in r or "offline" in s:
        return (
            "AI Summary:\n"
            "Camera feed is unavailable.\n\n"
            "AI Suggestion:\n"
            "Check camera source, network, and restart camera.\n\n"
            "AI Decision Support:\n"
            "Restore camera connection before relying on monitoring."
        )

    return (
        "AI Summary:\n"
        "Camera status reviewed.\n\n"
        "AI Suggestion:\n"
        "Continue monitoring.\n\n"
        "AI Decision Support:\n"
        "User should verify final action."
    )


def generate_camera_ai_summary(camera_id, status, result, frames, same_tiger=""):
    print("ENTERED generate_camera_ai_summary")
    print("GEMINI_API_KEY:", "FOUND" if GEMINI_API_KEY else "MISSING")

    if not GEMINI_API_KEY:
        print("USING LOCAL AI: GEMINI_API_KEY missing")
        return local_camera_ai_summary(camera_id, status, result, frames, same_tiger)

    try:
        print("USING GEMINI AI for", camera_id)

        prompt = f"""
You are Tiger AI Assistant for a Tiger Detection Monitoring System.

Camera: {camera_id}
Status: {status}
Last Result: {result}
Frames Checked: {frames}
Same Tiger Status: {same_tiger}

Generate dynamic output exactly in this format:

AI Summary:
...

AI Suggestion:
...

AI Decision Support:
...

Keep it short, simple, and practical.
Do not give long explanation.
Final real-world action must be done by user.
"""

        response = gemini_model.generate_content(prompt)

        print("GEMINI RESPONSE:", response.text)

        return response.text

    except Exception as e:
        print("GEMINI ERROR:", e)
        return local_camera_ai_summary(camera_id, status, result, frames, same_tiger)


def ai_decision_support(result, camera_id="System", message=""):
    return generate_camera_ai_summary(
        camera_id=camera_id,
        status="Detection Completed",
        result=result,
        frames="N/A",
        same_tiger=message
    )