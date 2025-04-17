from http.server import SimpleHTTPRequestHandler, HTTPServer
import urllib.parse
import json
import Admin

sock = Admin.connect()

class AdminHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers['Content-Length'])
        body = self.rfile.read(length).decode()
        data = urllib.parse.parse_qs(body)

        action = data.get('action', [''])[0]
        name = data.get('name', [''])[0]
        password = data.get('password', [''])[0]
        app_name = data.get('app_name', [''])[0]

        response = "OK"

        if action == "identify":
            Admin.identification(sock, name, password)
            response = "OK"
        elif action == "add":
            Admin.add_to_db(sock, "APPS", app_name)
        elif action == "remove":
            Admin.remove_from_db(sock, "APPS", f"name = {app_name}")
        else:
            response = "Invalid action"

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": response}).encode())

    def do_GET(self):
        if self.path == "/":
            self.path = "/admin_website.html"
        return super().do_GET()

if __name__ == "__main__":
    httpd = HTTPServer(('0.0.0.0', 8080), AdminHandler)
    print("Serving at http://localhost:8080")
    httpd.serve_forever()
