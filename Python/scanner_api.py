from flask import Flask, request, jsonify
import detailedScan
import os

app = Flask(__name__)

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
        result_path = 'wieye_app/lib/DetailedResult.json'
        if not os.path.exists(result_path):
            return jsonify({'error': 'Scan failed or file not found'}), 500

        with open(result_path, 'r') as f:
            return f.read(), 200, {'Content-Type': 'application/json'}

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
