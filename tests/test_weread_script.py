import os
import subprocess
import threading
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer
import json


ROOT = Path(__file__).resolve().parents[1]


def test_weread_script_without_api_key_fails_safely(tmp_path):
    env = os.environ.copy()
    env.pop("WEREAD_API_KEY", None)
    env["HOME"] = str(tmp_path)
    result = subprocess.run(
        [str(ROOT / "scripts" / "weread.sh"), "shelf"],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 3
    assert "缺少 WEREAD_API_KEY" in result.stderr
    assert "wrk-" not in result.stdout


def test_weread_script_prints_gateway_error_body():
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            self.send_response(499, "ERR")
            self.end_headers()
            self.wfile.write(b'{"errCode":499,"errMsg":"bad request"}')

        def log_message(self, format, *args):
            return

    server = HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        env = os.environ.copy()
        env["WEREAD_API_KEY"] = "wrk-test"
        env["WEREAD_GATEWAY"] = f"http://127.0.0.1:{server.server_port}"
        result = subprocess.run(
            [str(ROOT / "scripts" / "weread.sh"), "shelf"],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
        )
    finally:
        server.shutdown()

    assert result.returncode == 4
    assert "WeRead API HTTP 499: ERR" in result.stderr
    assert "bad request" in result.stderr
    assert "Traceback" not in result.stderr
    assert "wrk-test" not in result.stderr


def test_weread_script_flattens_business_params():
    requests = []

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            length = int(self.headers["Content-Length"])
            requests.append(json.loads(self.rfile.read(length)))
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"ok":true}')

        def log_message(self, format, *args):
            return

    server = HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        env = os.environ.copy()
        env["WEREAD_API_KEY"] = "wrk-test"
        env["WEREAD_GATEWAY"] = f"http://127.0.0.1:{server.server_port}"
        result = subprocess.run(
            [str(ROOT / "scripts" / "weread.sh"), "notebooks", "--count=20"],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
        )
    finally:
        server.shutdown()

    assert result.returncode == 0
    assert requests == [{"api_name": "/user/notebooks", "skill_version": "1.0.3", "count": 20}]
    assert "params" not in requests[0]


def test_weread_script_reads_api_key_file_when_env_missing(tmp_path):
    requests = []

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            requests.append(self.headers.get("Authorization"))
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"ok":true}')

        def log_message(self, format, *args):
            return

    key_dir = tmp_path / ".config" / "carl-weread"
    key_dir.mkdir(parents=True)
    key_file = key_dir / "api_key"
    key_file.write_text("wrk-file-key\n", encoding="utf-8")
    key_file.chmod(0o600)

    server = HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        env = os.environ.copy()
        env.pop("WEREAD_API_KEY", None)
        env["HOME"] = str(tmp_path)
        env["WEREAD_GATEWAY"] = f"http://127.0.0.1:{server.server_port}"
        result = subprocess.run(
            [str(ROOT / "scripts" / "weread.sh"), "shelf"],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
        )
    finally:
        server.shutdown()

    assert result.returncode == 0
    assert requests == ["Bearer wrk-file-key"]
    assert "wrk-file-key" not in result.stdout
    assert "wrk-file-key" not in result.stderr
