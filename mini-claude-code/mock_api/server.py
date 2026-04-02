#!/usr/bin/env python3
"""Mock API Server for mini-claude-code demo"""

import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")

with open(DATA_FILE) as f:
    DATA = json.load(f)


class MockAPIHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"[MockAPI] {args[0]}")

    def send_json(self, payload, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode())

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path == "/api/prices":
            symbols = query.get("symbols", ["BTC", "ETH", "AAPL", "GOOGL", "TSLA"])
            result = {s: DATA["prices"].get(s, 0.0) for s in symbols}
            self.send_json({"prices": result})

        elif path == "/api/files":
            file_path = query.get("path", ["/data/sample.txt"])[0]
            content = DATA["files"].get(file_path, f"File not found: {file_path}")
            self.send_json({"path": file_path, "content": content})

        elif path == "/api/env":
            key = query.get("key", [None])[0]
            if key:
                result = DATA["env"].get(key, f"ENV not found: {key}")
            else:
                result = DATA["env"]
            self.send_json({"env": result})

        elif path == "/api/health":
            self.send_json({"status": "ok", "service": "mock_api"})

        else:
            self.send_json({"error": "Unknown endpoint", "path": path}, 404)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), MockAPIHandler)
    print(f"[MockAPI] Starting server on port {port}")
    server.serve_forever()
