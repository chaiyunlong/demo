import json
from http.server import BaseHTTPRequestHandler

from resume_agent import analyze_request
from resume_agent.core import ResumeGrowthAdvisor


def analyze_payload(payload):
    advisor = ResumeGrowthAdvisor()
    result = analyze_request(payload)
    return {"markdown": advisor.render_markdown(result), "result": result}


class handler(BaseHTTPRequestHandler):
    def _send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers.get("content-length", "0"))
        raw_body = self.rfile.read(content_length).decode("utf-8") if content_length else "{}"
        try:
            payload = json.loads(raw_body or "{}")
            self._send_json(200, analyze_payload(payload))
        except json.JSONDecodeError as exc:
            self._send_json(400, {"error": f"Invalid JSON: {exc}"})
        except Exception as exc:
            self._send_json(500, {"error": str(exc)})
