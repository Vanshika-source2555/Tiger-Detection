import os
import time

def delete_old_files(folder_path, hours=24):
    if not os.path.exists(folder_path):
        return f"{folder_path} not found"

    now = time.time()
    max_age = hours * 60 * 60
    deleted = 0

    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)

        if os.path.isfile(file_path):
            age = now - os.path.getmtime(file_path)

            if age > max_age:
                os.remove(file_path)
                deleted += 1

    return f"{deleted} old files deleted from {folder_path}"