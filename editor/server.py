import http.server
import socketserver
import json

PORT = 8000

current_payload = "{}"


def update_payload(json_string):
    global current_payload
    current_payload = json_string


class MalletHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        # spits out whatever is currently in memory
        self.wfile.write(current_payload.encode("utf-8"))


def start():
    with socketserver.TCPServer(("", PORT), MalletHandler) as httpd:
        print(f"Mallet local bridge running at http://localhost:{PORT}")
        httpd.serve_forever()