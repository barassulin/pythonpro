import http.server
import socketserver
import urllib.parse

PORT = 8000

users = {}  # username: password
user_data = {  # fake user data
    "john": [111, 222],
    "jane": [333, 444]
}

details = {  # number -> phones and addresses
    111: {"phones": ["111-111", "111-222"], "addresses": ["1 First St", "2 Second St"]},
    222: {"phones": ["222-111"], "addresses": ["3 Third St"]},
    333: {"phones": ["333-333", "333-444"], "addresses": ["4 Fourth St"]},
    444: {"phones": ["444-111"], "addresses": ["5 Fifth St"]},
}


class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.path = "/index.html"
        elif self.path.startswith("/home"):
            self.path = "/home.html"
        elif self.path.startswith("/details"):
            self.path = "/details.html"
            print("p")
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        length = int(self.headers['Content-Length'])
        data = self.rfile.read(length).decode()
        params = urllib.parse.parse_qs(data)

        if self.path == "/login":
            username = params.get("username", [""])[0]
            password = params.get("password", [""])[0]
            action = params.get("action", [""])[0]

            if action == "signup":
                users[username] = password
                self.send_response(301)
                self.send_header("Location", f"/home?user={username}")
                self.end_headers()
            elif action == "signin":
                if users.get(username) == password:
                    self.send_response(301)
                    self.send_header("Location", f"/home?user={username}")
                    self.end_headers()
                else:
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b"Invalid login")
        elif self.path == "/pick":
            number = params.get("number", [""])[0]
            self.send_response(301)
            self.send_header("Location", f"/details?number={number}")
            self.end_headers()


Handler = MyHandler
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("Serving at port", PORT)
    httpd.serve_forever()
