import subprocess
import time
import os

print("\n🔐 Honeypot AI System — Starting Up...\n")

# === Paths (ensure you're in correct directory) ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

# === Launch components ===
processes = []

try:
    print("[1] Starting Suricata Simulator (suricata.py)...")
    p1 = subprocess.Popen(["python", "suricata.py"])
    processes.append(p1)

    time.sleep(1)

    print("[2] Starting Real-Time ML Detector (realtime.py)...")
    p2 = subprocess.Popen(["python", "realtime.py"])
    processes.append(p2)

    time.sleep(1)

    print("[3] Launching Web Dashboard (dashboard.py)...")
    p3 = subprocess.Popen(["python", "dashboard.py"])
    processes.append(p3)

    print("\n✅ All services started. Visit: http://127.0.0.1:5000\n")
    print("🛑 Press Ctrl+C to stop all components.")

    # === Wait forever ===
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\n[!] Shutting down all components...")
    for p in processes:
        p.terminate()
    print("✅ All processes terminated.")

except Exception as e:
    print(f"[!] Error: {e}")
