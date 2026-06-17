import mysql.connector

try:
    con = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="tiger_detection_db"
    )

    print("Connected Successfully")

except Exception as e:
    print(e)