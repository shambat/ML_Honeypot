import json
import time
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from joblib import load

# === File paths ===
DATASET_FILE = "dataset.csv"
ALERT_FILE = "eve.json"
OUTPUT_FILE = "output.csv"
MODEL_FILE = "classifier.pkl"

# === Step 1: Load dataset.csv to fit LabelEncoders ===
print("[*] Loading dataset.csv for dynamic encoding...")
dataset = pd.read_csv(DATASET_FILE)

label_encoders = {}
for col in ['src_ip', 'dest_ip', 'protocol', 'signature']:
    le = LabelEncoder()
    dataset[col] = le.fit_transform(dataset[col])
    label_encoders[col] = le

# === Step 2: Load trained model ===
print("[*] Loading trained model from classifier.pkl...")
model = load(MODEL_FILE)

# === Step 3: Prepare output file ===
try:
    with open(OUTPUT_FILE, "x") as f:
        f.write("src_ip,dest_ip,protocol,signature,status\n")
except FileExistsError:
    pass  # Already exists, no problem

# === Step 4: Real-time detection loop ===
print("[*] Starting real-time detection...")

seen_lines = set()

def classify_entry(entry_raw):
    try:
        # Encode using label encoders from dataset.csv
        encoded = {}
        for col in ['src_ip', 'dest_ip', 'protocol', 'signature']:
            le = label_encoders[col]
            val = entry_raw[col]
            if val not in le.classes_:
                print(f"[!] Unknown value in column '{col}': {val}")
                return None  # skip unknown
            encoded[col] = le.transform([val])[0]

        X = pd.DataFrame([encoded])
        prediction = model.predict(X)[0]
        entry_raw['status'] = "Malicious" if prediction == 1 else "Benign"
        return entry_raw

    except Exception as e:
        print(f"[!] Error classifying entry: {e}")
        return None

# === Step 5: Monitor and process eve.json ===
def monitor_eve_json():
    while True:
        try:
            with open(ALERT_FILE, 'r') as f:
                for line in f:
                    if line not in seen_lines:
                        seen_lines.add(line)
                        try:
                            alert = json.loads(line)
                            if 'alert' not in alert:
                                continue
                            entry_raw = {
                                'src_ip': alert['src_ip'],
                                'dest_ip': alert['dest_ip'],
                                'protocol': alert['proto'],
                                'signature': alert['alert']['signature']
                            }
                            result = classify_entry(entry_raw)
                            if result:
                                pd.DataFrame([result]).to_csv(OUTPUT_FILE, mode='a', header=False, index=False)
                                print(f"[+] Classified and saved: {result}")
                        except json.JSONDecodeError:
                            continue
        except FileNotFoundError:
            print("[!] eve.json not found. Waiting...")
        time.sleep(2)

if __name__ == "__main__":
    monitor_eve_json()
