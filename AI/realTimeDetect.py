import pyshark
import joblib
import numpy as np
import pandas as pd
import time
import traceback
from sklearn.preprocessing import StandardScaler
import os
import requests
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Python')))
from networkManagement import blockUser


# Load the trained model and preprocessing tools
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "ping_scan_detection_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "scaler.pkl")
ENCODER_PATH = os.path.join(BASE_DIR, "label_encoders.pkl")

logRegModel = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)
encoders = joblib.load(ENCODER_PATH)

# Define the network interface for packet capture
networkInterface = r"\Device\NPF_{A20B8C6B-B55A-4AA9-9699-C129F992E46B}" #Ethernet 2
#networkInterface = r"\Device\NPF_{46D9FA86-FE63-4E98-8BDD-D9D389631807}"

# Original
# r"\Device\NPF_{28DF2159-9CD6-475C-977B-40917DC2795C}"

# Load whitelist IPs
try:
    with open(os.path.join(BASE_DIR,"whiteListDevice.txt"), "r") as f:
        whiteListIPs = set(line.strip() for line in f if line.strip())
except FileNotFoundError:
    print("[!] Whitelist file not found. Continuing without whitelist.")
    whiteListIPs = set()

# Helper: safe encoding
def safeEncode(value, encoder):
    valStr = str(value)
    return encoder.transform([valStr])[0] if valStr in encoder.classes_ else -1

# Extract features from a packet
def extractFeatures(packet):
    try:
        srcIp = "N/A"
        dstIp = "N/A"
        srcPort = 0
        dstPort = 0
        length = int(packet.length) if hasattr(packet, 'length') else 0
        flowDuration = 0
        protocol = "UNKNOWN"

        # Handle IP packets
        if hasattr(packet, 'ip'):
            srcIp = packet.ip.src
            dstIp = packet.ip.dst
            protocol = str(packet.transport_layer) if hasattr(packet, 'transport_layer') and packet.transport_layer else "UNKNOWN"
            if packet.transport_layer:
                try:
                    srcPort = int(packet[packet.transport_layer].srcport)
                    dstPort = int(packet[packet.transport_layer].dstport)
                except (AttributeError, ValueError):
                    srcPort = 0
                    dstPort = 0

        # Handle ARP packets
        elif hasattr(packet, 'arp'):
            srcIp = packet.arp.src_proto_ipv4
            dstIp = packet.arp.dst_proto_ipv4
            protocol = "ARP"

        # Skip if IPs are invalid or whitelisted
        if (
                srcIp == "N/A" or dstIp == "N/A" or
                srcIp in whiteListIPs or dstIp in whiteListIPs
        ):
            return None, None, None, None, None

        # Encode features
        srcPortEncoded = safeEncode(srcPort, encoders["Source Port"])
        dstPortEncoded = safeEncode(dstPort, encoders["Destination Port"])
        protocolEncoded = safeEncode(protocol, encoders["Protocol"])

        features = pd.DataFrame([[length, srcPortEncoded, dstPortEncoded, flowDuration, protocolEncoded]],
                                columns=["Length", "Source Port", "Destination Port", "Flow Duration", "Protocol"])
        features = scaler.transform(features)

        # Build info text
        infoText = f"{srcIp}:{srcPort} → {dstIp}:{dstPort} [{protocol}] Length={length}"
        if hasattr(packet, 'tcp'):
            flags = []
            if hasattr(packet.tcp, 'flags_syn') and packet.tcp.flags_syn == '1':
                flags.append("SYN")
            if hasattr(packet.tcp, 'flags_ack') and packet.tcp.flags_ack == '1':
                flags.append("ACK")
            if hasattr(packet.tcp, 'flags_fin') and packet.tcp.flags_fin == '1':
                flags.append("FIN")
            if flags:
                infoText += f" [{'|'.join(flags)}]"
            if hasattr(packet.tcp, 'seq') and hasattr(packet.tcp, 'ack'):
                infoText += f" Seq={packet.tcp.seq} Ack={packet.tcp.ack}"

        return features, infoText, srcIp, dstIp, length
    except Exception as e:
        print(f"Error processing packet: {e}")
        traceback.print_exc()
        return None, None, None, None, None

# Capture and classify live traffic
def captureLiveTraffic():
    print("[+] Starting real-time network traffic capture...")

    maliciousLengths = {}  # length → timestamp
    TIME_WINDOW = 10  # seconds

    capture = pyshark.LiveCapture(interface=networkInterface)

    for packet in capture:
        features, infoText, srcIp, dstIp, lengthValue = extractFeatures(packet)
        if features is None:
            continue

        currentTime = time.time()

        # Remove expired lengths
        expired = [l for l, t in maliciousLengths.items() if currentTime - t > TIME_WINDOW]
        for l in expired:
            del maliciousLengths[l]

        # SKIP EVERYTHING if length was flagged recently
        if lengthValue in maliciousLengths:
            continue

        # Only predict if not recently flagged
        prediction = logRegModel.predict(features)
        if prediction[0] == 1:
            maliciousLengths[lengthValue] = currentTime
            result = "Malicious"
        else:
            result = "Normal Traffic"

        print(f"[+] Classification: {result} | {infoText}")

        # Notify Flask server
        if result == "Malicious":
            try:
                requests.post("http://127.0.0.1:5000/trigger-malware", json={"info": infoText})
                requests.post("http://127.0.0.1:5000/block-device", json={"ip": srcIp})
            except Exception as e:
                print(f"[!] Failed to notify: {e}")

# Entry point
if __name__ == "__main__":
    captureLiveTraffic()