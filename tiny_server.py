"""
Bar Assulin ~ 27/5/25
for checking
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os

apps_list = [
    {"id": 1, "name": "instagram"},
    {"id": 2, "name": "pinterest"},
    {"id": 3, "name": "chrome2"},
    {"id": 4, "name": "spotify2"},
]


class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 1) JSON list endpoint
        if self.path == '/get-apps-list':
            payload = json.dumps(apps_list).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        # 2) HTML page endpoint
        if self.path in ('/', '/apps.html'):
            file_path = os.path.join('C:/serveriii/webroot', 'apps.html')
            try:
                with open(file_path, 'rb') as f:
                    html = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(html)))
                self.end_headers()
                self.wfile.write(html)
            except FileNotFoundError:
                self.send_error(404, "apps.html not found")
            return

        # 3) All other requests = 404
        self.send_error(404, "Not Found")

    def do_POST(self):
        # (Your remove/add handlers go here…)
        self.send_error(404, "Not Found")


if __name__ == '__main__':
    HTTPServer(('localhost', 8000), SimpleHandler).serve_forever()
