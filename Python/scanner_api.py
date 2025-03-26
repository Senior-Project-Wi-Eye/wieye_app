from flask import Flask, request, jsonify
import detailedScan
import OSScan
import quickIPScan
import os
import threading

app = Flask(__name__)

def start_background_scans():
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
        result_path = '../lib/DetailedResult.json'
        if not os.path.exists(result_path):
            return jsonify({'error': 'Scan failed or file not found'}), 500

        with open(result_path, 'r') as f:
            return f.read(), 200, {'Content-Type': 'application/json'}

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    start_background_scans()
    app.run(host='0.0.0.0', port=5000)
