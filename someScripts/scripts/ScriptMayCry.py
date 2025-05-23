import http.server
import socketserver
import threading
import socket
import cv2
import os
import webbrowser

PORT = 88
VIDEO_PATH = "Trolling Saruman.mp4"  # Replace with your video file path

def play_video():
    if not os.path.exists(VIDEO_PATH):
        print(f"Video file not found: {VIDEO_PATH}")
        return

    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        print("Error opening video file")
        return

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow("Video", frame)
        if cv2.waitKey(25) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        client_ip = self.client_address[0]
        print(f"Connection from {client_ip}")

        if client_ip != "127.0.0.1":
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b"Access denied: Only localhost is allowed.")
            return

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"<html><body><h1>Video playing...</h1></body></html>")

        # Start video playback in a new thread to avoid blocking
        threading.Thread(target=play_video, daemon=True).start()

def run_server():
    with socketserver.TCPServer(("0.0.0.0", PORT), CustomHandler) as httpd:
        print(f"Serving on port {PORT} (localhost only access)")
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()

    # webbrowser.open("http://127.0.0.1:88/")
