import http.server
import socketserver
import os

PORT = 88
VIDEO_FILE = "Trolling Saruman.mp4"  # Make sure this file exists in the same folder

class VideoRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.client_address[0] != "127.0.0.1":
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b"Access denied: localhost only.")
            return

        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            html = f"""
            <html>
            <head><title>Video Player</title></head>
            <body>
                <h1>Localhost Video Player</h1>
                <video width="720" controls autoplay>
                    <source src="/{VIDEO_FILE}" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            </body>
            </html>
            """
            self.wfile.write(html.encode("utf-8"))
        else:
            # Serve the video file or other assets normally
            super().do_GET()

if __name__ == "__main__":
    if not os.path.exists(VIDEO_FILE):
        print(f"Video file '{VIDEO_FILE}' not found.")
        exit(1)

    with socketserver.TCPServer(("0.0.0.0", PORT), VideoRequestHandler) as httpd:
        print(f"Serving on http://127.0.0.1:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
