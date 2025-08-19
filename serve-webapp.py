#!/usr/bin/env python3
"""
Simple HTTP server to serve the Web App
Serves on port 3000 to avoid conflict with API (port 8000)
"""
import os
import http.server
import socketserver
from pathlib import Path

# Set the directory to serve files from
WEBROOT = Path(__file__).parent / "webappadmin"
PORT = 3000

# Change to webroot directory
os.chdir(WEBROOT)

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers for API calls
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        # Handle preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def guess_type(self, path):
        mimetype = super().guess_type(path)
        if path.endswith('.html'):
            return 'text/html; charset=utf-8'
        return mimetype

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
        print(f"🌐 Web App Server starting...")
        print(f"📂 Serving files from: {WEBROOT}")
        print(f"🔗 Web App URL: http://localhost:{PORT}/customer_webapp.html")
        print(f"🛑 Press Ctrl+C to stop")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")