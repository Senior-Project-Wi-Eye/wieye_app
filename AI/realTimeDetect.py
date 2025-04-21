import pyshark
import joblib
import numpy as np
import pandas as pd
import time
import traceback
import csv
from sklearn.preprocessing import StandardScaler
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
            return None, None, None, None, None, None, None, None

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

        return features, infoText, srcIp, dstIp, length, srcPort, dstPort, protocol

    except Exception as e:
        print(f"Error processing packet: {e}")
        traceback.print_exc()
        return None, None, None, None, None, None, None, None

# Capture and classify live traffic
def captureLiveTraffic():
    print("[+] Starting real-time network traffic capture...")

    maliciousLengths = {}
    TIME_WINDOW = 0  # seconds

    # Create CSV with headers
    csvFile = os.path.join(BASE_DIR,"traffic_log.csv")
    with open(csvFile, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Source IP", "Source Port", "Destination IP", "Destination Port", "Protocol", "Length", "Classification"])

    capture = pyshark.LiveCapture(interface=networkInterface)

    for packet in capture:
        features, infoText, srcIp, dstIp, lengthValue, srcPort, dstPort, protocol = extractFeatures(packet)
        if features is None:
            continue

        timestamp = pd.Timestamp.now()

        # Automatically classify same-IP traffic as normal
        if srcIp == dstIp:
            result = "Normal Traffic"
            print(f"[+] Classification: {result} | {infoText}")

            with open(csvFile, mode='a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, srcIp, srcPort, dstIp, dstPort, protocol, lengthValue, result])
            continue

        currentTime = time.time()

        # Remove expired lengths
        expired = [l for l, t in maliciousLengths.items() if currentTime - t > TIME_WINDOW]
        for l in expired:
            del maliciousLengths[l]

        # Skip recently flagged lengths
        if lengthValue in maliciousLengths:
            continue

        # Predict traffic type
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
                # Send malware detection notification
                requests.post("http://127.0.0.1:5000/trigger-malware", json={"info": infoText})

                # Block the user
                blockUser(srcIp)

                # Send a success notification
                requests.post("http://127.0.0.1:5000/trigger-notification", json={
                    "title": "Device Blocked",
                    "body": f"{srcIp} has been successfully blocked due to suspicious activity."
                })

            except Exception as e:
                print(f"[!] Failed to notify: {e}")

        with open(csvFile, mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, srcIp, srcPort, dstIp, dstPort, protocol, lengthValue, result])

# Entry point
if __name__ == "__main__":
    captureLiveTraffic()