from flask import Flask, Response, render_template_string, request, redirect, url_for, session, jsonify
import pandas as pd
import json
import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

app = Flask(__name__)
app.secret_key = 'super_secret_key'  # Required for session management
OUTPUT_FILE = "output.csv"
last_mtime = [0]  # Mutable list to track file modification time
CRED_FILE = "cred.txt"

# === Load Credentials ===
def load_credentials():
    try:
        with open(CRED_FILE, 'r') as f:
            for line in f:
                username, password = line.strip().split(':')
                return username, password
        return None, None
    except FileNotFoundError:
        print(f"[!] {CRED_FILE} not found")
        return None, None
    except Exception as e:
        print(f"[!] Error reading {CRED_FILE}: {e}")
        return None, None

# === Login Page HTML ===
LOGIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - Real-Time ML Alert Dashboard</title>
    <style>
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            color: #333;
        }
        .login-container {
            background-color: #ffffff;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
            width: 100%;
            max-width: 400px;
            text-align: center;
        }
        h1 {
            font-size: 28px;
            margin-bottom: 10px;
            color: #2c3e50;
        }
        h2 {
            font-size: 16px;
            color: #7f8c8d;
            margin-bottom: 30px;
            font-weight: normal;
        }
        .form-group {
            margin-bottom: 20px;
            text-align: left;
        }
        label {
            display: block;
            font-size: 14px;
            color: #34495e;
            margin-bottom: 8px;
            font-weight: 500;
        }
        input[type="text"], input[type="password"] {
            width: 100%;
            padding: 12px;
            border: 1px solid #dcdcdc;
            border-radius: 6px;
            font-size: 16px;
            box-sizing: border-box;
            transition: border-color 0.3s;
        }
        input[type="text"]:focus, input[type="password"]:focus {
            border-color: #667eea;
            outline: none;
            box-shadow: 0 0 5px rgba(102, 126, 234, 0.3);
        }
        input[type="submit"] {
            background-color: #667eea;
            color: white;
            padding: 12px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            width: 100%;
            font-size: 16px;
            font-weight: 600;
            transition: background-color 0.3s;
        }
        input[type="submit"]:hover {
            background-color: #5a6cd3;
        }
        .error {
            color: #e74c3c;
            font-size: 14px;
            margin-top: 10px;
            display: block;
        }
        .footer-text {
            margin-top: 20px;
            font-size: 12px;
            color: #7f8c8d;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <h1>ML Alert Dashboard</h1>
        <h2>Sign in to access real-time monitoring</h2>
        <form method="POST" action="{{ url_for('login') }}">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" placeholder="Enter username" required>
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" placeholder="Enter password" required>
            </div>
            {% if error %}
                <span class="error">{{ error }}</span>
            {% endif %}
            <input type="submit" value="Sign In">
        </form>
        <div class="footer-text">
            Secured access for authorized users only
        </div>
    </div>
</body>
</html>
"""

# === Dashboard HTML ===
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Real-Time ML Alert Dashboard</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f0f0f0;
            margin: 0;
            padding: 20px;
        }
        h1 {
            text-align: center;
            color: #333;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            background-color: #fff;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            margin-top: 20px;
        }
        th, td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #4CAF50;
            color: white;
        }
        tr:hover {
            background-color: #f5f5f5;
        }
        .malicious {
            color: red;
            font-weight: bold;
        }
        .benign {
            color: green;
        }
        .logout {
            position: absolute;
            top: 20px;
            right: 20px;
        }
        .logout a {
            color: #4CAF50;
            text-decoration: none;
            font-weight: bold;
        }
        .logout a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="logout">
        <a href="{{ url_for('logout') }}">Logout</a>
    </div>
    <h1>Real-Time ML Alert Dashboard</h1>
    <table id="alertTable">
        <thead>
            <tr>
                <th>Source IP</th>
                <th>Destination IP</th>
                <th>Protocol</th>
                <th>Signature</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody id="alertBody"></tbody>
    </table>

    <script>
        // Load initial data
        fetch('/initial-data')
            .then(response => response.json())
            .then(data => updateTable(data))
            .catch(error => console.error('Error loading initial data:', error));

        // Update table with data
        function updateTable(data) {
            const tbody = document.getElementById('alertBody');
            tbody.innerHTML = ''; // Clear existing rows
            data.forEach(row => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${row.src_ip}</td>
                    <td>${row.dest_ip}</td>
                    <td>${row.protocol}</td>
                    <td>${row.signature}</td>
                    <td class="${row.status.toLowerCase()}">${row.status}</td>
                `;
                tbody.appendChild(tr);
            });
        }

        // SSE for real-time updates
        const eventSource = new EventSource('/stream');
        eventSource.onmessage = function(event) {
            const data = JSON.parse(event.data);
            updateTable(data);
        };
        eventSource.onerror = function() {
            console.log('SSE error, retrying...');
        };
    </script>
</body>
</html>
"""

# === File Monitoring ===
class FileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(OUTPUT_FILE):
            last_mtime[0] = os.path.getmtime(OUTPUT_FILE)
            print(f"[*] Detected change in {OUTPUT_FILE}: mtime={last_mtime[0]}")

# Start file monitoring
def start_file_monitor():
    event_handler = FileHandler()
    observer = Observer()
    observer.schedule(event_handler, path=OUTPUT_FILE, recursive=False)
    observer.start()
    print("[*] File monitoring started for", OUTPUT_FILE)

# === Route Protection ===
def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or not session['logged_in']:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# === Routes ===
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username, password = load_credentials()
        if username is None or password is None:
            return render_template_string(LOGIN_HTML, error="Credentials file error")
        
        input_username = request.form.get('username')
        input_password = request.form.get('password')
        
        if input_username == username and input_password == password:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return render_template_string(LOGIN_HTML, error="Invalid credentials")
    
    return render_template_string(LOGIN_HTML, error=None)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template_string(DASHBOARD_HTML)

@app.route('/initial-data')
@login_required
def initial_data():
    try:
        df = pd.read_csv(OUTPUT_FILE, header=None, names=['src_ip', 'dest_ip', 'protocol', 'signature', 'status'])
        last_five = df.tail(5).to_dict(orient='records')
        print("[*] Initial data loaded:", last_five)
        return jsonify(last_five)
    except FileNotFoundError:
        print(f"[!] {OUTPUT_FILE} not found")
        return jsonify([])
    except Exception as e:
        print(f"[!] Error reading {OUTPUT_FILE}: {e}")
        return jsonify([])

@app.route('/stream')
@login_required
def stream():
    def generate():
        previous_mtime = last_mtime[0]
        while True:
            try:
                current_mtime = os.path.getmtime(OUTPUT_FILE)
                if current_mtime > previous_mtime:
                    df = pd.read_csv(OUTPUT_FILE, header=None, names=['src_ip', 'dest_ip', 'protocol', 'signature', 'status'])
                    last_five = df.tail(5).to_dict(orient='records')
                    print("[*] Streaming data:", last_five)
                    yield f"data: {json.dumps(last_five)}\n\n"
                    previous_mtime = current_mtime
                time.sleep(2)
            except FileNotFoundError:
                print(f"[!] {OUTPUT_FILE} not found")
            except Exception as e:
                print(f"[!] Error in stream: {e}")
                time.sleep(2)
    return Response(generate(), mimetype='text/event-stream')

if __name__ == "__main__":
    start_file_monitor()
    app.run(debug=True, host='0.0.0.0', port=5000)