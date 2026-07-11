#!/usr/bin/env python3
"""Tin OS submission runtime: browser home, AI app launcher, and tmux cockpit.

This is a sanitized single-node extraction of the live Tin operating pattern.
It intentionally uses only Python's standard library and fixed, auditable commands.
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import re
import shutil
import socket
import subprocess
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent
WEB_ROOT = ROOT / "web"
SESSION_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_.@-]{0,63}$")
ALLOWED_AGENTS = {"bash", "opencode", "pi", "claude", "codex"}
OPENCODE_PORT = int(os.environ.get("TIN_OPENCODE_PORT", "2023"))
PI_WEB_PORT = int(os.environ.get("TIN_PI_WEB_PORT", "2024"))
WORKSPACE = Path(os.environ.get("TIN_WORKSPACE", str(Path.home()))).expanduser().resolve()
LOG_DIR = Path(os.environ.get("TIN_LOG_DIR", str(Path.home() / ".local/state/tin-os"))).expanduser()


def run(args: list[str], *, timeout: int = 8, check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, text=True, capture_output=True, timeout=timeout, check=check)


def port_open(port: int, host: str = "127.0.0.1") -> bool:
    try:
        with socket.create_connection((host, port), timeout=0.4):
            return True
    except OSError:
        return False


def command_path(name: str) -> str | None:
    direct = shutil.which(name)
    if direct:
        return direct
    candidates = {
        "opencode": [Path.home() / ".opencode/bin/opencode", Path.home() / ".local/bin/opencode"],
        "pi-web-server": [Path.home() / ".local/bin/pi-web-server"],
        "pi-web-sessiond": [Path.home() / ".local/bin/pi-web-sessiond"],
    }
    for path in candidates.get(name, []):
        if path.is_file() and os.access(path, os.X_OK):
            return str(path)
    return None


def tmux_available() -> bool:
    return command_path("tmux") is not None


def list_sessions() -> list[dict]:
    if not tmux_available():
        return []
    result = run(["tmux", "list-sessions", "-F", "#{session_name}\t#{session_attached}\t#{session_created}"], timeout=5)
    if result.returncode != 0:
        return []
    sessions: list[dict] = []
    for row in result.stdout.splitlines():
        parts = row.split("\t")
        if len(parts) != 3:
            continue
        name, attached, created = parts
        pane = run(["tmux", "list-panes", "-t", name, "-F", "#{pane_current_command}\t#{pane_current_path}\t#{pane_dead}"], timeout=5)
        pane_parts = (pane.stdout.splitlines() or ["\t\t"])[0].split("\t")
        command = pane_parts[0] if pane_parts else ""
        path = pane_parts[1] if len(pane_parts) > 1 else ""
        dead = len(pane_parts) > 2 and pane_parts[2] == "1"
        capture = run(["tmux", "capture-pane", "-p", "-t", name, "-S", "-24"], timeout=5)
        output = "\n".join(capture.stdout.rstrip().splitlines()[-24:])
        sessions.append(
            {
                "name": name,
                "attached": int(attached or 0),
                "created": int(created or 0),
                "command": command,
                "path": path,
                "dead": dead,
                "running": command not in {"", "bash", "zsh", "fish", "sh"},
                "output": output,
            }
        )
    return sorted(sessions, key=lambda item: item["created"], reverse=True)


def create_session(name: str, agent: str = "bash") -> dict:
    if not SESSION_RE.fullmatch(name):
        raise ValueError("Use 1–64 letters, numbers, dots, underscores, @, or hyphens.")
    if agent not in ALLOWED_AGENTS:
        raise ValueError(f"Unsupported agent: {agent}")
    if not tmux_available():
        raise RuntimeError("tmux is not installed")
    existing = {item["name"] for item in list_sessions()}
    if name in existing:
        return {"created": False, "name": name}
    args = ["tmux", "new-session", "-d", "-s", name, "-c", str(WORKSPACE)]
    if agent != "bash":
        binary = command_path(agent)
        if not binary:
            raise RuntimeError(f"{agent} is not installed")
        args.append(binary)
    result = run(args, timeout=10)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "tmux could not create the session")
    return {"created": True, "name": name}


def delete_session(name: str) -> None:
    if not SESSION_RE.fullmatch(name):
        raise ValueError("Invalid session name")
    result = run(["tmux", "kill-session", "-t", name], timeout=8)
    if result.returncode != 0 and "can't find session" not in result.stderr.lower():
        raise RuntimeError(result.stderr.strip() or "tmux could not stop the session")


def start_opencode() -> dict:
    if port_open(OPENCODE_PORT):
        return {"ready": True, "started": False, "port": OPENCODE_PORT}
    binary = command_path("opencode")
    if not binary:
        raise RuntimeError("OpenCode is not installed. Run install/install-ai-apps.sh first.")
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    run(["tmux", "kill-session", "-t", "tin-opencode-web"], timeout=4)
    result = run(
        ["tmux", "new-session", "-d", "-s", "tin-opencode-web", "-c", str(WORKSPACE), binary, "web", "--hostname", "0.0.0.0", "--port", str(OPENCODE_PORT)],
        timeout=10,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "OpenCode Web could not start")
    for _ in range(30):
        if port_open(OPENCODE_PORT):
            return {"ready": True, "started": True, "port": OPENCODE_PORT}
        time.sleep(0.25)
    raise RuntimeError("OpenCode Web did not become ready")


def start_pi_web() -> dict:
    if port_open(PI_WEB_PORT):
        return {"ready": True, "started": False, "port": PI_WEB_PORT}
    web = command_path("pi-web-server")
    sessiond = command_path("pi-web-sessiond")
    if not web or not sessiond:
        raise RuntimeError("Pi Web is not installed. Run install/install-ai-apps.sh first.")
    run(["tmux", "kill-session", "-t", "tin-pi-sessiond"], timeout=4)
    run(["tmux", "kill-session", "-t", "tin-pi-web"], timeout=4)
    first = run(["tmux", "new-session", "-d", "-s", "tin-pi-sessiond", sessiond], timeout=10)
    if first.returncode != 0:
        raise RuntimeError(first.stderr.strip() or "Pi Web session daemon could not start")
    env = [
        "/usr/bin/env",
        "PI_WEB_HOST=0.0.0.0",
        f"PI_WEB_PORT={PI_WEB_PORT}",
        "PI_WEB_ALLOWED_HOSTS=true",
        web,
    ]
    second = run(["tmux", "new-session", "-d", "-s", "tin-pi-web", *env], timeout=10)
    if second.returncode != 0:
        raise RuntimeError(second.stderr.strip() or "Pi Web could not start")
    for _ in range(40):
        if port_open(PI_WEB_PORT):
            return {"ready": True, "started": True, "port": PI_WEB_PORT}
        time.sleep(0.25)
    raise RuntimeError("Pi Web did not become ready")


def module_status() -> dict:
    return {
        "opencode": {"installed": command_path("opencode") is not None, "ready": port_open(OPENCODE_PORT), "port": OPENCODE_PORT},
        "pi": {
            "installed": command_path("pi-web-server") is not None and command_path("pi-web-sessiond") is not None,
            "ready": port_open(PI_WEB_PORT),
            "port": PI_WEB_PORT,
        },
        "tmux": {"installed": tmux_available(), "sessions": len(list_sessions())},
    }


def host_for_url(value: str) -> str:
    host = value.split(":", 1)[0].strip("[]")
    return host if host not in {"", "0.0.0.0", "127.0.0.1", "localhost"} else socket.gethostname()


class Handler(BaseHTTPRequestHandler):
    server_version = "TinOS/0.2"

    def log_message(self, fmt: str, *args: object) -> None:
        print(f"[{self.log_date_time_string()}] {self.address_string()} {fmt % args}")

    def json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0") or 0)
        if length > 64 * 1024:
            raise ValueError("Request body too large")
        return json.loads(self.rfile.read(length) or b"{}")

    def send_json(self, data: object, status: int = 200) -> None:
        raw = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def error_json(self, error: Exception, status: int = 400) -> None:
        self.send_json({"error": str(error)}, status)

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/api/status":
            sessions = list_sessions()
            self.send_json(
                {
                    "node": socket.gethostname(),
                    "workspace": str(WORKSPACE),
                    "sessions": len(sessions),
                    "running": sum(1 for item in sessions if item["running"]),
                    "modules": module_status(),
                }
            )
            return
        if path == "/api/sessions":
            self.send_json(list_sessions())
            return
        self.serve_static(path)

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        try:
            if path == "/api/sessions":
                body = self.json_body()
                self.send_json(create_session(str(body.get("name", "")), str(body.get("agent", "bash"))), 201)
                return
            if path == "/api/modules/opencode/start":
                result = start_opencode()
                result["url"] = f"http://{host_for_url(self.headers.get('Host', ''))}:{OPENCODE_PORT}/"
                self.send_json(result)
                return
            if path == "/api/modules/pi/start":
                result = start_pi_web()
                result["url"] = f"http://{host_for_url(self.headers.get('Host', ''))}:{PI_WEB_PORT}/"
                self.send_json(result)
                return
            self.send_json({"error": "Not found"}, HTTPStatus.NOT_FOUND)
        except (ValueError, RuntimeError, subprocess.SubprocessError) as exc:
            self.error_json(exc, HTTPStatus.CONFLICT)

    def do_DELETE(self) -> None:  # noqa: N802
        path = unquote(urlparse(self.path).path)
        prefix = "/api/sessions/"
        if not path.startswith(prefix):
            self.send_json({"error": "Not found"}, HTTPStatus.NOT_FOUND)
            return
        try:
            delete_session(path[len(prefix) :])
            self.send_json({"deleted": True})
        except (ValueError, RuntimeError, subprocess.SubprocessError) as exc:
            self.error_json(exc, HTTPStatus.CONFLICT)

    def serve_static(self, request_path: str) -> None:
        relative = "index.html" if request_path in {"", "/"} else request_path.lstrip("/")
        candidate = (WEB_ROOT / relative).resolve()
        try:
            candidate.relative_to(WEB_ROOT.resolve())
        except ValueError:
            self.send_error(HTTPStatus.FORBIDDEN)
            return
        if not candidate.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        raw = candidate.read_bytes()
        content_type = mimetypes.guess_type(candidate.name)[0] or "application/octet-stream"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-cache" if candidate.suffix in {".html", ".js", ".css"} else "public, max-age=86400")
        self.end_headers()
        self.wfile.write(raw)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Tin OS browser home and tmux cockpit")
    parser.add_argument("--host", default=os.environ.get("TIN_HOST", "0.0.0.0"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("TIN_PORT", "8080")))
    args = parser.parse_args()
    WORKSPACE.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Tin OS ready: http://127.0.0.1:{args.port} (workspace: {WORKSPACE})")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
