from datetime import datetime

def format_bytes(bytes_value):
    for unit in ['B','KB','MB','GB','TB']:
        if bytes_value < 1024:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024
    return f"{bytes_value:.1f} PB"

def current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
