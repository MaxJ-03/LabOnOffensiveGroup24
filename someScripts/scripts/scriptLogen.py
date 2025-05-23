import http.server
import socketserver
import os
import socket
from urllib.parse import parse_qs

PORT = 88
VIDEO_FILE = "Trolling Saruman.mp4"
USERNAME = "admin"
PASSWORD = "1234"

sessions = set()

class VideoRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        ip = self.client_address[0]
        if self.path == "/" or self.path == "/login":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(self.login_page().encode("utf-8"))

        elif self.path == "/video":
            if ip not in sessions:
                self.redirect_to_login()
                return

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            html = f"""
            <html>
            <head>
                <title>Video Player</title>
                <style>
                    html, body {{
                        margin: 0;
                        padding: 0;
                        height: 100%;
                        overflow: hidden;
                        background-color: #000;
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        justify-content: center;
                    }}
                    h1 {{
                        color: white;
                        margin: 10px 0;  /* Smaller header space */
                        font-size: 1.2em;
                    }}
                    video {{
                        width: 1280px;
                        height: 720px;
                        max-width: 100%;
                        pointer-events: none;  /* Makes the video unclickable = unpausable */
                    }}
                </style>
            </head>
            <body>
                <h1>Bravo na {USERNAME}</h1>
                <video autoplay playsinline>
                    <source src="/{VIDEO_FILE}" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            </body>
            </html>
            """

            self.wfile.write(html.encode("utf-8"))

        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/login":
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length).decode("utf-8")
            params = parse_qs(body)

            username = params.get("username", [""])[0]
            password = params.get("password", [""])[0]

            if username == USERNAME and password == PASSWORD:
                sessions.add(self.client_address[0])
                self.send_response(302)
                self.send_header("Location", "/video")
                self.end_headers()
            else:
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b"Login failed")
    
    def login_page(self):
        return f"""
        <html>
        <head>
            <title>IPCam Client</title>
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                    height: 100%;
                    width: 100%;
                    font-family: Arial, sans-serif;
                    background: url('/The-identical-fake-login-page.ppm') no-repeat center center fixed;
                    background-size: cover;
                    position: relative;
                    overflow: hidden;
                    color: #000;
                }}
                form {{
                    width: 180px;
                    margin: 255px 0 0 725px;
                    padding: 0;
                }}
                input[type="text"],
                input[type="password"],
                select {{
                    width: 75%;
                    padding: 5px 6px;
                    margin-bottom: 32px;
                    border: 1px solid #aaa;
                    border-radius: 4px;
                    background: rgba(255, 255, 255, 0.9);
                    font-size: 12px;
                    box-sizing: border-box;
                    outline: none;
                }}
                input[type="text"]:focus,
                input[type="password"]:focus,
                select:focus {{
                    border-color: #666;
                    background: rgba(255, 255, 255, 0.9);
                }}
                input[type="submit"] {{
                    width: 90px;
                    margin-left: 130px;
                    padding: 8px;
                    background: linear-gradient(to bottom, #aaa, #666);
                    color: black;
                    border: none;
                    border-radius: 4px;
                    font-size: 14px;
                    cursor: pointer;
                    box-sizing: border-box;
                }}
                input[type="submit"]:hover {{
                    background: linear-gradient(to bottom, #999, #444);
                }}
                label {{
                    display: none;
                }}
            </style>
        </head>
        <body>
            <form method="POST" action="/login">
                <input type="text" id="username" name="username" value="admin" placeholder="Username">
                <input type="password" id="password" name="password" placeholder="Password">
                <select name="stream" id="stream" aria-label="Stream">
                    <option>Main stream</option>
                    <option>Sub stream</option>
                </select>
                <select name="language" id="language" aria-label="Language">
                    <option>English</option>
                </select>
                <input type="submit" value="Login">
            </form>
        </body>
        </html>
        """

    # def login_page(self):
    #     return f"""
    #     <html>
    #     <head>
    #         <title>IPCam Client</title>
    #         <style>
    #             html, body {{
    #                 margin: 0;
    #                 padding: 0;
    #                 height: 100%;
    #                 width: 100%;
    #                 font-family: Arial, sans-serif;
    #                 background: url('/The-identical-fake-login-page.ppm') no-repeat center center fixed;
    #                 background-size: cover;
    #                 display: flex;
    #                 justify-content: center;
    #                 align-items: center;
    #             }}
    #             form {{
    #                 width: 18vw;
    #                 min-width: 180px;
    #                 max-width: 280px;
    #                 padding: 1rem;
    #                 padding-left: 100px;
    #                 box-sizing: border-box;
    #                 display: flex;
    #                 flex-direction: column;
    #                 align-items: flex-start;
    #                 margin-top: 15vh;              /* ← moves the form down */
    #             }}
    #             input[type="text"],
    #             input[type="password"],
    #             select {{
    #                 width: 88%;
    #                 padding: 0.4em 0.6em;
    #                 margin-bottom: 1.75rem;
    #                 border: 1px solid #aaa;
    #                 border-radius: 4px;
    #                 background: rgba(255, 255, 255, 0.9);
    #                 font-size: 0.85rem;
    #                 box-sizing: border-box;
    #                 outline: none;
    #             }}
    #             input[type="submit"] {{
    #                 /* align-self: flex-end; */
    #                 margin-left: 130px; 
    #                 padding: 0.5em 2em;
    #                 background: linear-gradient(to bottom, #aaa, #666);
    #                 color: black;
    #                 border: none;
    #                 border-radius: 4px;
    #                 font-size: 0.9rem;
    #                 cursor: pointer;
    #             }}
    #             input[type="submit"]:hover {{
    #                 background: linear-gradient(to bottom, #999, #444);
    #             }}
    #             label {{
    #                 display: none;
    #             }}
    #         </style>
    #     </head>
    #     <body>
    #         <form method="POST" action="/login">
    #             <input type="text" id="username" name="username" value="admin" placeholder="Username">
    #             <input type="password" id="password" name="password" placeholder="Password">
    #             <select name="stream" id="stream" aria-label="Stream">
    #                 <option>Main stream</option>
    #                 <option>Sub stream</option>
    #             </select>
    #             <select name="language" id="language" aria-label="Language">
    #                 <option>English</option>
    #             </select>
    #             <input type="submit" value="Login">
    #         </form>
    #     </body>
    #     </html>
    #     """

    def redirect_to_login(self):
        self.send_response(302)
        self.send_header("Location", "/login")
        self.end_headers()

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = "127.0.0.1"
    finally:
        s.close()
    return IP

if __name__ == "__main__":
    if not os.path.exists(VIDEO_FILE):
        print(f"Video file '{VIDEO_FILE}' not found.")
        exit(1)

    with socketserver.TCPServer(("0.0.0.0", PORT), VideoRequestHandler) as httpd:
        ip = get_local_ip()
        print(f"Serving on http://{ip}:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
