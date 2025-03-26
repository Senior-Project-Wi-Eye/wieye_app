import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Function to safely load a CSV file with different encodings
def load_csv_safe(file_path):
    encodings = ["utf-8", "ISO-8859-1", "Windows-1252", "utf-16"]
    for enc in encodings:
        try:
            return pd.read_csv(file_path, encoding=enc)
        except UnicodeDecodeError:
            print(f"Failed to read {file_path} with encoding {enc}, trying next...")
    print(f"All encoding attempts failed for {file_path}. Check file manually.")
    exit()

# Load datasets
df_ddos_syn = load_csv_safe("DDoSTCPSYNFlood.csv")
df_ping_scan = load_csv_safe("NmapPingScan.csv")
df_normal_traffic = load_csv_safe("NormalTraffic.csv")

# Assign labels
df_ddos_syn["Malicious"] = 1
df_ping_scan["Malicious"] = 1
df_normal_traffic["Malicious"] = 0

# Combine all datasets (now includes SYN flood)
df = pd.concat([df_ddos_syn, df_ping_scan, df_normal_traffic], ignore_index=True)

# Drop unnecessary columns (Info is kept for inspection if needed)
drop_columns = ["No.", "Time", "Source", "Destination", "Payload Size"]  # Exclude 'Info'
df.drop(columns=[col for col in drop_columns if col in df.columns], inplace=True, errors='ignore')

# Rename "Packet Length" to "Length" if needed
if "Packet Length" in df.columns:
    df.rename(columns={"Packet Length": "Length"}, inplace=True)

# Fill missing values
df.fillna(0, inplace=True)

# Initialize LabelEncoder
label_encoder = LabelEncoder()

# Encode Source and Destination Ports
for col in ["Source Port", "Destination Port", "Protocol"]:
    if col in df.columns:
        df[col] = df[col].astype(str)  # Ensure all are strings
        df[col] = label_encoder.fit_transform(df[col])

# Select features and labels
X = df[["Length", "Source Port", "Destination Port", "Flow Duration", "Protocol"]]
y = df["Malicious"]

print("\n[INFO] First 5 rows of training data (before standardization):")
print(X.head())

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Standardize
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Train the model
log_reg_model = LogisticRegression(max_iter=500, solver='lbfgs', random_state=42)
log_reg_model.fit(X_train, y_train)

# Save model and preprocessors
joblib.dump(log_reg_model, "ping_scan_detection_model.pkl")
joblib.dump(scaler, "scaler.pkl")
joblib.dump(label_encoder, "label_encoder.pkl")

print("\n[+] Model trained and saved successfully!")

# Evaluate
y_pred = log_reg_model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"\nModel Accuracy: {accuracy:.4f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))
