import pyshark
import joblib
import numpy as np
import pandas as pd
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

# Function to safely transform ports (handles unseen values)
def transform_port(port):
    """Encodes port number, returns -1 if unseen."""
    port_str = str(port)
    return label_encoder.transform([port_str])[0] if port_str in label_encoder.classes_ else -1

# Function to safely transform protocol (handles unseen values)
def transform_protocol(protocol):
    """Encodes protocol, returns -1 if unseen."""
    protocol_str = str(protocol)
    return label_encoder.transform([protocol_str])[0] if protocol_str in label_encoder.classes_ else -1

def extract_features(packet):
    try:
        if not hasattr(packet, 'transport_layer'):
            return None, None

        src_port = int(packet[packet.transport_layer].srcport) if hasattr(packet, 'tcp') or hasattr(packet, 'udp') else 0
        dst_port = int(packet[packet.transport_layer].dstport) if hasattr(packet, 'tcp') or hasattr(packet, 'udp') else 0
        length = int(packet.length) if hasattr(packet, 'length') else 0
        flow_duration = 0
        protocol = str(packet.transport_layer) if hasattr(packet, 'transport_layer') else "UNKNOWN"

        # Encode
        src_port_encoded = transform_port(src_port)
        dst_port_encoded = transform_port(dst_port)
        protocol_encoded = transform_protocol(protocol)

        features = pd.DataFrame([[length, src_port_encoded, dst_port_encoded, flow_duration, protocol_encoded]],
                                columns=["Length", "Source Port", "Destination Port", "Flow Duration", "Protocol"])
        features = scaler.transform(features)

        # Manually construct Info-like summary
        info_text = f"{src_port} → {dst_port} [{protocol}] Length={length}"
        if hasattr(packet, 'tcp') and hasattr(packet.tcp, 'flags_ack'):
            flags = []
            if hasattr(packet.tcp, 'flags_syn') and packet.tcp.flags_syn == '1':
                flags.append("SYN")
            if hasattr(packet.tcp, 'flags_ack') and packet.tcp.flags_ack == '1':
                flags.append("ACK")
            if hasattr(packet.tcp, 'flags_fin') and packet.tcp.flags_fin == '1':
                flags.append("FIN")
            flag_str = "|".join(flags)
            info_text += f" [{flag_str}]" if flag_str else ""

            if hasattr(packet.tcp, 'seq') and hasattr(packet.tcp, 'ack'):
                info_text += f" Seq={packet.tcp.seq} Ack={packet.tcp.ack}"

        return features, info_text
    except Exception as e:
        print(f"Error processing packet: {e}")
        return None, None

# Function to capture and classify packets in real-time
def capture_live_traffic():
    print("[+] Starting real-time network traffic capture...")
    capture = pyshark.LiveCapture(interface=NETWORK_INTERFACE)

    for packet in capture:
        features, info_text = extract_features(packet)
        if features is not None:
            prediction = log_reg_model.predict(features)
            result = "Malicious" if prediction[0] == 1 else "Normal Traffic"

            print(f"[+] Classification: {result} | Info: {info_text}")

            # Notify Flask server
            if result == "Malicious":
                try:
                    requests.post("http://127.0.0.1:5000/trigger-malware", json={"info": info_text})
                except Exception as e:
                    print(f"[!] Failed to notify: {e}")

# Run the live capture function
if __name__ == "__main__":
    capture_live_traffic()
