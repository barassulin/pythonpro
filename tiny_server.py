from http.server import HTTPServer, BaseHTTPRequestHandler
import json

apps_list = ["instegram", "chrome", "pinterest", "spotify"]

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/get-apps-list':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(apps_list).encode())
        elif self.path == '/':
            # Serve a simple HTML page
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"""
            <!DOCTYPE html>
            <html>
            <head><title>appss List</title></head>
            <body>
                <ul id="apps-list"></ul>
                <script>
                    var appsList = document.getElementById('apps-list');
                    fetch('/get-apps-list')
                        .then(response => response.json())
                        .then(data => {
                            data.forEach(item => {
                                var li = document.createElement('li');
                                li.textContent = item;
                                appsList.appendChild(li);
                            });
                        })
                        .catch(error => {
                            console.error('Error fetching apps list:', error);
                        });
                </script>
            </body>
            </html>
            """)
        else:
            self.send_response(404)
            self.end_headers()


if __name__ == '__main__':
    print("Serving on http://localhost:8000")
    httpd = HTTPServer(('localhost', 8000), SimpleHandler)
    httpd.serve_forever()