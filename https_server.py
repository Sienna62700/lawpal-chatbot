import http.server
import ssl

# Set up the HTTP server
handler = http.server.SimpleHTTPRequestHandler
httpd = http.server.HTTPServer(('127.0.0.1', 8001), handler)

# Enable HTTPS by wrapping the server with SSL
httpd.socket = ssl.wrap_socket(httpd.socket,
                               keyfile="mykey.key", certfile="mycert.crt", server_side=True)

print("Serving on https://localhost:8000")
httpd.serve_forever()
