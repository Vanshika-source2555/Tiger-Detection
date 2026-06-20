import os
import re
import openpyxl
import os
from anthropic import Anthropic

QA_FILE = "qa_dataset.xlsx"


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
    user_question_clean = clean_text(user_question)
    user_words = set(user_question_clean.split())

    best_score = 0
    best_answer = None

    for item in load_qa_dataset():
        dataset_words = set(item["clean_question"].split())

        score = len(user_words.intersection(dataset_words))

        if item["clean_question"] == user_question_clean:
            score += 30

        if user_question_clean in item["clean_question"]:
            score += 15

        if score > best_score:
            best_score = score
            best_answer = item["answer"]

    if best_score >= 1:
        return best_answer

    return None


def fallback_answer(question):
    return (
        "I can help with image detection, video detection, live camera, "
        "same tiger identification, alerts, history, reports, dataset, "
        "model training, backend, Java frontend, and troubleshooting.\n\n"
        "Suggestion:\n"
        "Ask a project-related question like camera, tiger, model, error, history, or stripe."
    )

def ai_chat_answer(question):
    answer = dataset_answer(question)

    if answer:
        return answer

    try:
        answer = claude_answer(question)
        if answer:
            return answer
    except Exception as e:
        print("Claude error:", e)

    return fallback_answer(question)
def claude_answer(question):
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        return None

    client = Anthropic(api_key=api_key)

    system_prompt = """
You are Tiger AI Assistant.
Give short, simple, and impactful answers.
Focus only on this Tiger Detection project:
image detection, video detection, live camera, same tiger identification,
alerts, history, reports, dataset, model training, backend, Java frontend,
and troubleshooting.
Give practical suggestions.
Final real-world action must be done by the user.
"""

    response = client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=250,
        system=system_prompt,
        messages=[
            {"role": "user", "content": question}
        ]
    )

    return response.content[0].text