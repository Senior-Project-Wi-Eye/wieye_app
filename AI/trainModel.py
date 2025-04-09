import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

def loadCsvSafe(filePath):
    encodings = ["utf-8", "ISO-8859-1", "Windows-1252", "utf-16"]
    for enc in encodings:
        try:
            return pd.read_csv(filePath, encoding=enc)
        except UnicodeDecodeError:
            print(f"Failed to read {filePath} with encoding {enc}, trying next...")
    print(f"All encoding attempts failed for {filePath}. Check file manually.")
    exit()

# Load datasets
dfDdosSyn = loadCsvSafe("DDoSTCPSYNFlood.csv")
dfPingScan = loadCsvSafe("NmapPingScan.csv")
dfNormalTraffic = loadCsvSafe("NormalTraffic.csv")

# Label the data
dfDdosSyn["Malicious"] = 1
dfPingScan["Malicious"] = 1
dfNormalTraffic["Malicious"] = 0

# Combine datasets
dfCombined = pd.concat([dfDdosSyn, dfPingScan, dfNormalTraffic], ignore_index=True)

# Drop unnecessary or identifier columns (especially IP addresses)
dropColumns = ["No.", "Time", "Source", "Destination", "Payload Size"]
dfCombined.drop(columns=[col for col in dropColumns if col in dfCombined.columns], inplace=True, errors='ignore')

# Rename for consistency
if "Packet Length" in dfCombined.columns:
    dfCombined.rename(columns={"Packet Length": "Length"}, inplace=True)

dfCombined.fillna(0, inplace=True)

# Encode categorical columns individually and save encoders
encoders = {}
for col in ["Source Port", "Destination Port", "Protocol"]:
    if col in dfCombined.columns:
        dfCombined[col] = dfCombined[col].astype(str)
        le = LabelEncoder()
        dfCombined[col] = le.fit_transform(dfCombined[col])
        encoders[col] = le

# Extract features and label
features = dfCombined[["Length", "Source Port", "Destination Port", "Flow Duration", "Protocol"]]
labels = dfCombined["Malicious"]

print("\n[INFO] First 5 rows of training data (before standardization):")
print(features.head())

# Split data
featuresTrain, featuresTest, labelsTrain, labelsTest = train_test_split(
    features, labels, test_size=0.2, random_state=42, stratify=labels
)

# Scale data
scaler = StandardScaler()
featuresTrain = scaler.fit_transform(featuresTrain)
featuresTest = scaler.transform(featuresTest)

# Train model
logRegModel = LogisticRegression(max_iter=500, solver='lbfgs', random_state=42)
logRegModel.fit(featuresTrain, labelsTrain)

# Save model and encoders
joblib.dump(logRegModel, "ping_scan_detection_model.pkl")
joblib.dump(scaler, "scaler.pkl")
joblib.dump(encoders, "label_encoders.pkl")

# Evaluate model
labelsPred = logRegModel.predict(featuresTest)
accuracy = accuracy_score(labelsTest, labelsPred)

print("\n[+] Model trained and saved successfully!")
print(f"\nModel Accuracy: {accuracy:.4f}")
print("\nClassification Report:")
print(classification_report(labelsTest, labelsPred))
print("\nConfusion Matrix:")
print(confusion_matrix(labelsTest, labelsPred))