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


# Run on two termials
# C:\Users\tyler\StudioProjects\wieye_app\Python\scanner_api.py
# C:\Users\tyler\StudioProjects\wieye_app\AI\realTimeDetect.py

app = Flask(__name__)

malware_detected = False
last_malware_info = ""


def start_background_scans():
    # change back if not on school wifi !!!! 10.15.159.179
    # 10.0.1.0/24

    threading.Thread(target=OSScan.constantOSScan, args=("10.0.1.0/24",), daemon=True).start()
    threading.Thread(target=quickIPScan.constantPingScan, args=("10.0.1.0/24",), daemon=True).start()

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
        FLUTTER_LIB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'wieye_app', 'lib'))
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

@app.route('/get-all-results', methods=['GET'])
def get_all_results():
    try:
        FLUTTER_LIB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'wieye_app', 'lib'))

        def load_json(file_name):
            file_path = os.path.join(FLUTTER_LIB_PATH, file_name)
            with open(file_path, 'r') as f:
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

    if not ip:
        return jsonify({'error': 'Missing IP'}), 400

    try:
        networkManagement.blockUser(ip)
        return jsonify({'status': 'Device blocked successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/scan-log', methods=['GET'])
def get_scan_log():
    return jsonify(scan_log)

@app.route('/notification-feed', methods=['GET'])
def get_custom_notifications():
    return jsonify(custom_notifications)

def graceful_shutdown(signal_received, frame):
    print("\n[INFO] Stopping background scans & shutting down Flask server...")
    sys.exit(0)

if __name__ == '__main__':
    # Attach shutdown handler
    signal.signal(signal.SIGINT, graceful_shutdown)
    signal.signal(signal.SIGTERM, graceful_shutdown)

    # Start background scanners
    start_background_scans()

    # Start Flask server
    app.run(host='0.0.0.0', port=5000)
