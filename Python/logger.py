# Python/logger.py
from datetime import datetime

scan_log = []

def log_event(msg):
    timestamped = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"
    # print(timestamped)
    scan_log.append(timestamped)
    if len(scan_log) > 50:
        scan_log.pop(0)
