import json
import time
import random
from datetime import datetime

# Output file
EVE_FILE = "eve.json"

# Random Pools
src_ips = [
    "192.168.1.10", "192.168.1.15", "10.0.0.5", "172.16.0.3",
    "172.16.1.22", "192.168.1.99", "10.10.10.10"
]
dest_ips = [
    "192.168.1.100", "192.168.1.200", "192.168.1.10", "192.168.1.50", "192.168.1.250"
]
protocols = ["TCP", "UDP", "ICMP"]
signatures = [
    "ET MALWARE Possible Malicious Traffic",
    "ET POLICY Suspicious DNS Query",
    "ET SCAN Suspicious Inbound to MSSQL port 1433",
    "ET SCAN ICMP Echo Detected",
    "ET TROJAN Fake Login Attempt",
    "ET EXPLOIT Possible Apache Struts RCE",
    "ET DOS DNS Amplification Attack",
    "ET WORM Conficker.A Checkin",
    "ET CNC ZeuS Bot Command and Control"
]

def generate_alert():
    alert = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "src_ip": random.choice(src_ips),
        "dest_ip": random.choice(dest_ips),
        "proto": random.choice(protocols),
        "alert": {
            "signature": random.choice(signatures)
        }
    }
    return alert

def simulate_suricata_alerts(filename=EVE_FILE, min_delay=1, max_delay=5):
    print("[*] Simulating randomized Suricata alerts... Press Ctrl+C to stop.")
    try:
        while True:
            alert = generate_alert()
            with open(filename, 'a') as f:
                f.write(json.dumps(alert) + '\n')
            print(f"[+] Alert written: {alert['src_ip']} → {alert['dest_ip']} | {alert['alert']['signature']}")
            time.sleep(random.randint(min_delay, max_delay))
    except KeyboardInterrupt:
        print("\n[!] Simulation stopped by user.")

if __name__ == "__main__":
    simulate_suricata_alerts()
