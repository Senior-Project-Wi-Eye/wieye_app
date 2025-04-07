import pyshark
import joblib
import numpy as np
import pandas as pd
import time
from sklearn.preprocessing import StandardScaler, LabelEncoder
import os
import requests

# Load the trained model and preprocessing tools
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "ping_scan_detection_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "scaler.pkl")
ENCODER_PATH = os.path.join(BASE_DIR, "label_encoder.pkl")

log_reg_model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)
label_encoder = joblib.load(ENCODER_PATH)

#log_reg_model = joblib.load("ping_scan_detection_model.pkl")
#scaler = joblib.load("scaler.pkl")
#label_encoder = joblib.load("label_encoder.pkl")

# Define the network interface for packet capture
NETWORK_INTERFACE = r"\Device\NPF_{46D9FA86-FE63-4E98-8BDD-D9D389631807}"

# Original
# r"\Device\NPF_{28DF2159-9CD6-475C-977B-40917DC2795C}"

# Load whitelist
try:
    with open("whiteListDevice.txt", "r") as f:
        whiteListIPs = set(line.strip() for line in f if line.strip())
except FileNotFoundError:
    print("[!] Whitelist file not found. Continuing without whitelist.")
    whiteListIPs = set()

# Function to safely transform ports (handles unseen values)
def transformPort(port):
    portStr = str(port)
    return labelEncoder.transform([portStr])[0] if portStr in labelEncoder.classes_ else -1

# Function to safely transform protocol (handles unseen values)
def transformProtocol(protocol):
    protocolStr = str(protocol)
    return labelEncoder.transform([protocolStr])[0] if protocolStr in labelEncoder.classes_ else -1

# Extract features from a packet
def extractFeatures(packet):
    try:
        if not hasattr(packet, 'transport_layer'):
            return None, None, None, None, None

        srcIp = packet.ip.src if hasattr(packet, 'ip') else "N/A"
        dstIp = packet.ip.dst if hasattr(packet, 'ip') else "N/A"
        srcPort = int(packet[packet.transport_layer].srcport) if hasattr(packet, 'tcp') or hasattr(packet, 'udp') else 0
        dstPort = int(packet[packet.transport_layer].dstport) if hasattr(packet, 'tcp') or hasattr(packet, 'udp') else 0
        length = int(packet.length) if hasattr(packet, 'length') else 0
        flowDuration = 0
        protocol = str(packet.transport_layer) if hasattr(packet, 'transport_layer') else "UNKNOWN"

        srcPortEncoded = transformPort(srcPort)
        dstPortEncoded = transformPort(dstPort)
        protocolEncoded = transformProtocol(protocol)

        features = pd.DataFrame([[length, srcPortEncoded, dstPortEncoded, flowDuration, protocolEncoded]],
                                columns=["Length", "Source Port", "Destination Port", "Flow Duration", "Protocol"])
        features = scaler.transform(features)

        infoText = f"{srcIp}:{srcPort} → {dstIp}:{dstPort} [{protocol}] Length={length}"
        if hasattr(packet, 'tcp') and hasattr(packet.tcp, 'flags_ack'):
            flags = []
            if hasattr(packet.tcp, 'flags_syn') and packet.tcp.flags_syn == '1':
                flags.append("SYN")
            if hasattr(packet.tcp, 'flags_ack') and packet.tcp.flags_ack == '1':
                flags.append("ACK")
            if hasattr(packet.tcp, 'flags_fin') and packet.tcp.flags_fin == '1':
                flags.append("FIN")
            flagStr = "|".join(flags)
            infoText += f" [{flagStr}]" if flagStr else ""

            if hasattr(packet.tcp, 'seq') and hasattr(packet.tcp, 'ack'):
                infoText += f" Seq={packet.tcp.seq} Ack={packet.tcp.ack}"

        return features, infoText, srcIp, dstIp, length
    except Exception as e:
        print(f"Error processing packet: {e}")
        return None, None, None, None, None

# Real-time packet classification
def captureLiveTraffic():
    print("[+] Starting real-time network traffic capture...")

    maliciousLengths = {}  # length: timestamp
    TIME_WINDOW = 20  # seconds

    capture = pyshark.LiveCapture(interface=networkInterface)

    for packet in capture:
        features, infoText, srcIp, dstIp, lengthValue = extractFeatures(packet)
        if features is not None:
            currentTime = time.time()

            # Remove expired malicious lengths
            expired = [l for l, t in maliciousLengths.items() if currentTime - t > TIME_WINDOW]
            for l in expired:
                del maliciousLengths[l]

            if srcIp in whiteListIPs or srcIp == "N/A":
                result = "Normal Traffic (Whitelisted or No Source IP)"
            elif lengthValue in maliciousLengths:
                result = "Malicious (Length Recently Flagged)"
            else:
                prediction = logRegModel.predict(features)
                if prediction[0] == 1:
                    result = "Malicious"
                    if lengthValue is not None:
                        maliciousLengths[lengthValue] = currentTime
                else:
                    result = "Normal Traffic"

            print(f"[+] Classification: {result} | Info: {infoText} | Source IP: {srcIp} | Destination IP: {dstIp}")

            # Notify Flask server
            if result == "Malicious":
               try:
                  requests.post("http://127.0.0.1:5000/trigger-malware", json={"info": info_text})
               except Exception as e:
                  print(f"[!] Failed to notify: {e}")

# Run the live capture function
if __name__ == "__main__":
    captureLiveTraffic()