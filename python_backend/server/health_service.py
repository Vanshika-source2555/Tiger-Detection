import psutil
import shutil

def get_server_health():
    disk = shutil.disk_usage(".")

    return {
        "cpu_usage": psutil.cpu_percent(interval=1),
        "ram_usage": psutil.virtual_memory().percent,
        "disk_usage": round((disk.used / disk.total) * 100, 2),
        "server_status": "Running"
    }