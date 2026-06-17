import mysql.connector
from db_config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME


def get_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )


def ensure_tables():
    db = get_connection()
    cursor = db.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(100) NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS detection_history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100),
            source_type VARCHAR(50),
            file_name VARCHAR(255),
            result VARCHAR(50),
            confidence DOUBLE,
            image_path VARCHAR(500),
            detected_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("DESCRIBE users")
    columns = [row[0] for row in cursor.fetchall()]

    if "email" not in columns and "username" in columns:
        cursor.execute("ALTER TABLE users CHANGE username email VARCHAR(100) UNIQUE NOT NULL")

    db.commit()
    cursor.close()
    db.close()


def signup_user(email, password):
    try:
        ensure_tables()

        db = get_connection()
        cursor = db.cursor()

        cursor.execute(
            "INSERT INTO users(email, password) VALUES(%s, %s)",
            (email, password)
        )

        db.commit()
        cursor.close()
        db.close()

        return "Signup successful"

    except mysql.connector.IntegrityError:
        return "Email already registered"

    except Exception as e:
        return "Database error: " + str(e)


def login_user(email, password):
    try:
        ensure_tables()

        db = get_connection()
        cursor = db.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (email, password)
        )

        user = cursor.fetchone()

        cursor.close()
        db.close()

        if user:
            return "success"

        return "Invalid email or password"

    except Exception as e:
        return "Database error: " + str(e)


def change_password(email, old_password, new_password):
    try:
        ensure_tables()

        db = get_connection()
        cursor = db.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (email, old_password)
        )

        user = cursor.fetchone()

        if user:
            cursor.execute(
                "UPDATE users SET password=%s WHERE email=%s",
                (new_password, email)
            )
            db.commit()
            message = "Password changed successfully"
        else:
            message = "Old password is incorrect"

        cursor.close()
        db.close()

        return message

    except Exception as e:
        return "Database error: " + str(e)


def save_detection(username, source_type, file_name, result, confidence, image_path):
    try:
        ensure_tables()

        db = get_connection()
        cursor = db.cursor()

        cursor.execute("""
            INSERT INTO detection_history
            (username, source_type, file_name, result, confidence, image_path)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (username, source_type, file_name, result, confidence, image_path))

        db.commit()
        cursor.close()
        db.close()

    except Exception as e:
        print("Error saving detection:", e)


def get_history():
    try:
        ensure_tables()

        db = get_connection()
        cursor = db.cursor()

        cursor.execute("""
            SELECT username, source_type, file_name, result, confidence, detected_time
            FROM detection_history
            ORDER BY id DESC
            LIMIT 50
        """)

        rows = cursor.fetchall()

        cursor.close()
        db.close()

        if not rows:
            return "No history found"

        text = "User | Source | File | Result | Confidence | Time\n"
        text += "-" * 90 + "\n"

        for row in rows:
            text += f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]}\n"

        return text

    except Exception as e:
        return "Database error: " + str(e)


def get_stats():
    try:
        ensure_tables()

        db = get_connection()
        cursor = db.cursor()

        cursor.execute("SELECT COUNT(*) FROM detection_history")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM detection_history WHERE result='Tiger'")
        tiger = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM detection_history WHERE result='Non-Tiger' OR result='NonTiger'")
        nontiger = cursor.fetchone()[0]

        cursor.close()
        db.close()

        return (
            f"Total Detections: {total}\n"
            f"Tiger Detected: {tiger}\n"
            f"Non-Tiger Detected: {nontiger}\n"
        )

    except Exception as e:
        return "Database error: " + str(e)


def get_user_stats(username):
    try:
        ensure_tables()

        db = get_connection()
        cursor = db.cursor()

        cursor.execute("SELECT COUNT(*) FROM detection_history WHERE username=%s", (username,))
        total = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM detection_history WHERE username=%s AND result='Tiger'",
            (username,)
        )
        tiger = cursor.fetchone()[0]

        cursor.close()
        db.close()

        return f"Total Detections: {total}\nTiger Detections: {tiger}"

    except Exception as e:
        return "Database error: " + str(e)