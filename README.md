# 🔐 Honeypot AI — Real-Time Intrusion Detection & Threat Classification

This project demonstrates a real-time intrusion detection and alert classification system using simulated Suricata alerts and a pre-trained machine learning model. It includes an auto-updating Flask-based dashboard for visualizing threat activity within a monitored network.

---

## 📁 Project Structure

Place all the following files in a single directory (e.g., `D:\AI_Honeypot`):

| File Name        | Purpose                                                                 |
|------------------|-------------------------------------------------------------------------|
| `suricata.py`     | Simulates dynamic Suricata alerts in `eve.json`                         |
| `realtime.py`     | Classifies alerts using a trained ML model                              |
| `dashboard.py`    | Web-based UI showing latest classified alerts                           |
| `start.py`        | Master script to launch all modules                                     |
| `classifier.pkl`  | Pre-trained scikit-learn model for classification                       |
| `dataset.csv`     | Used for fitting label encoders                                         |
| `output.csv`      | Final output of classified alerts *(auto-generated)*                    |
| `eve.json`        | Simulated Suricata alert file *(auto-generated)*                        |
| `cred.txt`        | Contains credentials or API keys used by modules *(if applicable)*      |

---

## ⚙️ Environment Setup

1. **Install Python 3.7+**

2. **Install required Python libraries:**
   ```bash
   pip3 install flask pandas scikit-learn joblib
   ```

---

## ▶️ Running the System

1. Open **Command Prompt** or **terminal**  
2. Navigate to the project directory:
   ```bash
   cd D:\AI_Honeypot
   ```

3. Start the full pipeline:
   ```bash
   python3 start.py
   ```

This command will automatically:
- Start simulated Suricata alerts (`suricata.py`)
- Begin real-time classification (`realtime.py`)
- Launch the local web dashboard (`dashboard.py`)

---

## 🌐 Accessing the Dashboard

Once running, open your browser and visit:

🔗 [http://127.0.0.1:5000](http://127.0.0.1:5000)

- The dashboard auto-refreshes every 5 seconds  
- Displays the **5 most recent classified alerts** from `output.csv`

---

## ⛔ Stopping the System

To stop all services, press:

```
Ctrl + C
```

in the terminal window.

---

## ✅ Output Format

Each row in `output.csv` has the following structure:

```text
src_ip,dest_ip,protocol,signature,status
192.168.1.10,192.168.1.100,TCP,ET MALWARE Possible Malicious Traffic,Malicious
```

Where `status` is predicted as:

- `Malicious`
- `Benign`

by the trained machine learning model (`classifier.pkl`).

---

## 📌 Notes

- The `cred.txt` file is used to store API keys or credentials, if any modules require authentication or external service access.
- This project is designed for **educational and demonstration purposes** in network security and machine learning-based threat detection.

---

## 🧠 Author

**Muhammad Ehtisham**  
Cybersecurity Enthusiast | SOC Analyst | AI Threat Detection Researcher  

---

## 🛡️ License

This project is released under the [MIT License](LICENSE).
