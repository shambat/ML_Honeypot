import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from joblib import dump

# === Load Dataset ===
df = pd.read_csv("dataset.csv")

# === Encode Features ===
le_src = LabelEncoder()
le_dst = LabelEncoder()
le_proto = LabelEncoder()
le_sig = LabelEncoder()

df['src_ip'] = le_src.fit_transform(df['src_ip'])
df['dest_ip'] = le_dst.fit_transform(df['dest_ip'])
df['protocol'] = le_proto.fit_transform(df['protocol'])
df['signature'] = le_sig.fit_transform(df['signature'])

# === Train/Test Split ===
X = df[['src_ip', 'dest_ip', 'protocol', 'signature']]
y = df['label']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# === Train Model ===
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# === Evaluate ===
y_pred = model.predict(X_test)
print("\n[+] Classification Report:\n")
print(classification_report(y_test, y_pred))

# === Save Model ===
dump(model, "classifier.pkl")
print("\n[+] Model saved as classifier.pkl")
