#!/usr/bin/env python3
"""Simple HTTP server for the frontend."""

import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler to serve the frontend files."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(Path(__file__).parent), **kwargs)
    
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def main():
    """Start the frontend server."""
    PORT = 5001
    
    print("🌐 Starting Frontend Server...")
    print(f"📁 Serving files from: {Path(__file__).parent}")
    print(f"🔗 Frontend URL: http://localhost:{PORT}")
    print(f"🔗 API Backend: http://localhost:8000")
    print("\n✅ Make sure your FastAPI backend is running on port 8000")
    print("💡 Press Ctrl+C to stop the server\n")
    
    try:
        with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
            print(f"🚀 Frontend server running at http://localhost:{PORT}")
            
            # Try to open browser automatically
            try:
                webbrowser.open(f'http://localhost:{PORT}')
                print("🌍 Browser opened automatically")
            except:
                print(f"🌍 Please open http://localhost:{PORT} in your browser")
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n👋 Frontend server stopped")
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ Port {PORT} is already in use")
            print("💡 Try stopping other servers or use a different port")
        else:
            print(f"❌ Server error: {e}")

if __name__ == "__main__":
    main()
