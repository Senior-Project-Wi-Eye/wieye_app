from flask import Flask, request, jsonify
import detailedScan
import OSScan
import quickIPScan
import networkManagement
from logger import log_event, scan_log
import os
import threading
import signal
import sys
import logging
import time
import json

app = Flask(__name__)

FLUTTER_LIB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'wieye_app', 'lib'))

malware_detected = False
last_malware_info = ""
custom_notifications = []

def start_background_scans():
    bgIp = "10.0.1.0/24"

    threading.Thread(target=OSScan.constantOSScan, args=(bgIp,), daemon=True).start()
    threading.Thread(target=quickIPScan.constantPingScan, args=(bgIp,), daemon=True).start()

@app.route('/scan', methods=['POST'])
def scan_device():
    try:
        data = request.json
        ip = data.get('ip')

        if not ip:
            return jsonify({'error': 'IP is required'}), 400

        # Set the target dynamically and scan
        detailedScan.target = ip
        detailedScan.nmapScan(ip)

        # Read result JSON and return it
        filename = os.path.join(FLUTTER_LIB_PATH, 'DetailedResult.json')

        if not os.path.exists(filename):
            return jsonify({'error': 'Scan failed or file not found'}), 500

        with open(filename, 'r') as f:
            return f.read(), 200, {'Content-Type': 'application/json'}

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/malware-alert', methods=['GET'])
def get_malware_alert():
    global malware_detected, last_malware_info
    if malware_detected:
        malware_detected = False

        return jsonify({"malware": True, "info": last_malware_info})
    return jsonify({"malware": False})

@app.route('/trigger-malware', methods=['POST'])
def trigger_malware():
    global malware_detected, last_malware_info
    data = request.json
    malware_detected = True
    last_malware_info = data.get('info', 'Suspicious Traffic Detected')
    return jsonify({"status": "alert triggered"})


@app.route('/trigger-notification', methods=['POST'])
def trigger_custom_notification():
    data = request.json
    title = data.get("title", "Alert")
    body = data.get("body", "")

    custom_notifications.append({
        "title": title,
        "body": body,
        "timestamp": time.time()
    })
    return jsonify({"status": "notification queued"})

@app.route('/notification-feed', methods=['GET'])
def get_custom_notifications():
    global custom_notifications
    to_send = custom_notifications.copy()
    custom_notifications = []
    return jsonify(to_send)

@app.route('/get-all-results', methods=['GET'])
def get_all_results():
    try:
        def load_json(file_name):
            filename = os.path.join(FLUTTER_LIB_PATH, file_name)
            with open(filename, 'r') as f:
                return f.read()

        ip_result = load_json('IPResult.json')
        os_result = load_json('OSResult.json')
        detailed_result = load_json('DetailedResult.json')

        return jsonify({
            "ip_result": ip_result,
            "os_result": os_result,
            "detailed_result": detailed_result
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/block-device', methods=['POST'])
def block_device():
    data = request.json
    ip = data.get('ip')
    print(ip)

    if not ip:
        return jsonify({'error': 'Missing IP'}), 400

    try:
        networkManagement.blockUser(ip)

        custom_notifications.append({
            "title": "Device Blocked",
            "body": f"{ip} was blocked.",
            "timestamp": time.time()
        })

        return jsonify({'status': f'{ip} - Device blocked successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get-blocked-devices', methods=['GET'])
def get_blocked_devices():
    filename = os.path.join(FLUTTER_LIB_PATH, 'BlockedDevices.json')
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/unblock-device', methods=['POST'])
def unblock_device():
    data = request.get_json()
    mac_to_remove = data.get("mac")
    if not mac_to_remove:
        return jsonify({"error": "Missing MAC address"}), 400

    try:
        from networkManagement import unblockUser
        unblockUser(mac_to_remove)
        return jsonify({"status": f"{mac_to_remove} unblocked"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/scan-log', methods=['GET'])
def get_scan_log():
    return jsonify(scan_log)

def graceful_shutdown(signal_received, frame):
    print("\n[INFO] Stopping background scans & shutting down Flask server...")
    sys.exit(0)

if __name__ == '__main__':
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)


# Attach shutdown handler
    signal.signal(signal.SIGINT, graceful_shutdown)
    signal.signal(signal.SIGTERM, graceful_shutdown)

    # Start background scanners
    start_background_scans()

    # Start Flask server
    app.run(host='0.0.0.0', port=5000)
