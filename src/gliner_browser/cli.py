from __future__ import annotations

import argparse
import json
import os
import re
import socket
import socketserver
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from .resolver import GlinerResolver
from .runtime import BrowserRuntime

MODEL_NAME = "fastino/gliner2.5-multi-v1"
ELEMENT_ID = re.compile(r"^@?e\d+$")


def state_dir() -> Path:
    configured = os.environ.get("GLINER_BROWSER_STATE_DIR")
    return Path(configured).expanduser() if configured else Path.home() / ".local/state/gliner-browser"


def send(request: dict[str, Any]) -> dict[str, Any]:
    path = state_dir() / "browser.sock"
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
        client.settimeout(float(os.environ.get("GLINER_BROWSER_TIMEOUT", "180")))
        client.connect(str(path))
        client.sendall(json.dumps(request).encode() + b"\n")
        chunks = []
        while chunk := client.recv(65536):
            chunks.append(chunk)
    return json.loads(b"".join(chunks))


def running() -> bool:
    try:
        return send({"command": "status"}).get("ok", False)
    except (ConnectionError, FileNotFoundError, OSError, TimeoutError, json.JSONDecodeError):
        return False


class Controller:
    def __init__(self, profile: Path, *, headless: bool) -> None:
        self.runtime = BrowserRuntime(profile, headless=headless)
        self.resolver = GlinerResolver(os.environ.get("GLINER_BROWSER_MODEL", MODEL_NAME))
        self.stopping = False

    def resolve(self, target: str) -> tuple[str, dict[str, Any] | None]:
        if ELEMENT_ID.fullmatch(target):
            return target.removeprefix("@"), None
        elements = self.runtime.observe(limit=300)["elements"]
        matches = self.resolver.find(target, elements)
        if not matches:
            raise LookupError(f"No interactive element matched {target!r}")
        return matches[0]["id"], matches[0]

    def handle(self, request: dict[str, Any]) -> dict[str, Any]:
        command = request.get("command")
        if command == "status":
            return {"ok": True, "running": True, "model": self.resolver.model_name}
        if command == "stop":
            self.stopping = True
            return {"ok": True, "stopping": True}
        if command == "open":
            return {"ok": True, **self.runtime.open(request["url"])}
        if command == "observe":
            return {"ok": True, **self.runtime.observe(request.get("limit", 100))}
        if command == "find":
            elements = self.runtime.observe(limit=300)["elements"]
            return {"ok": True, "matches": self.resolver.find(request["query"], elements)}
        if command in {"click", "fill", "select"}:
            element_id, match = self.resolve(request["target"])
            if command == "click":
                result = self.runtime.click(element_id)
            elif command == "fill":
                result = self.runtime.fill(element_id, request["text"])
            else:
                result = self.runtime.select(element_id, request["value"])
            return {"ok": True, **result, "match": match}
        if command == "press":
            return {"ok": True, **self.runtime.press(request["key"])}
        if command == "scroll":
            return {"ok": True, **self.runtime.scroll(request["pixels"])}
        if command == "screenshot":
            return {"ok": True, **self.runtime.screenshot(Path(request["path"]))}
        if command == "tabs":
            return {"ok": True, **self.runtime.tabs()}
        if command == "use-tab":
            return {"ok": True, **self.runtime.use_tab(request["index"])}
        raise ValueError(f"Unknown command: {command!r}")

    def close(self) -> None:
        self.runtime.close()


class RequestHandler(socketserver.BaseRequestHandler):
    def handle(self) -> None:
        raw = b""
        while b"\n" not in raw:
            chunk = self.request.recv(65536)
            if not chunk or len(raw) + len(chunk) > 1_000_000:
                break
            raw += chunk
        try:
            request = json.loads(raw.split(b"\n", 1)[0])
            response = self.server.controller.handle(request)  # type: ignore[attr-defined]
        except Exception as error:
            response = {"ok": False, "error": str(error), "type": type(error).__name__}
        self.request.sendall(json.dumps(response).encode())


class BrowserServer(socketserver.UnixStreamServer):
    allow_reuse_address = True


def serve(headless: bool) -> int:
    directory = state_dir()
    directory.mkdir(parents=True, exist_ok=True)
    os.chmod(directory, 0o700)
    socket_path = directory / "browser.sock"
    socket_path.unlink(missing_ok=True)
    controller = Controller(directory / "profile", headless=headless)
    server = BrowserServer(str(socket_path), RequestHandler)
    server.controller = controller  # type: ignore[attr-defined]
    try:
        while not controller.stopping:
            server.handle_request()
    finally:
        server.server_close()
        controller.close()
        socket_path.unlink(missing_ok=True)
    return 0


def start(headless: bool) -> dict[str, Any]:
    if running():
        return {"ok": True, "running": True, "already_running": True}
    directory = state_dir()
    directory.mkdir(parents=True, exist_ok=True)
    socket_path = directory / "browser.sock"
    socket_path.unlink(missing_ok=True)
    log = (directory / "daemon.log").open("ab")
    subprocess.Popen(
        [
            sys.executable,
            "-m",
            "gliner_browser.cli",
            "_serve",
            *(["--headless"] if headless else []),
        ],
        stdin=subprocess.DEVNULL,
        stdout=log,
        stderr=log,
        start_new_session=True,
    )
    log.close()
    for _ in range(150):
        if running():
            return {"ok": True, "running": True, "headless": headless}
        time.sleep(0.1)
    raise RuntimeError(f"Browser daemon did not start; inspect {directory / 'daemon.log'}")


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="gliner-browser")
    commands = root.add_subparsers(dest="command", required=True)
    start_command = commands.add_parser("start")
    start_command.add_argument("--headless", action="store_true")
    serve_command = commands.add_parser("_serve", help="internal daemon process")
    serve_command.add_argument("--headless", action="store_true")
    commands.add_parser("status")
    commands.add_parser("stop")
    open_command = commands.add_parser("open")
    open_command.add_argument("url")
    observe = commands.add_parser("observe")
    observe.add_argument("--limit", type=int, default=100)
    find = commands.add_parser("find")
    find.add_argument("query")
    for name in ("click", "fill", "select"):
        action = commands.add_parser(name)
        action.add_argument("target")
        if name == "fill":
            action.add_argument("text")
        if name == "select":
            action.add_argument("value")
    press = commands.add_parser("press")
    press.add_argument("key")
    scroll = commands.add_parser("scroll")
    scroll.add_argument("pixels", type=int, nargs="?", default=700)
    screenshot = commands.add_parser("screenshot")
    screenshot.add_argument("path")
    commands.add_parser("tabs")
    use_tab = commands.add_parser("use-tab")
    use_tab.add_argument("index", type=int)
    return root


def main() -> int:
    arguments = vars(parser().parse_args())
    command = arguments.pop("command")
    try:
        if command == "_serve":
            return serve(arguments["headless"])
        if command == "start":
            response = start(arguments["headless"])
        elif command == "status" and not running():
            response = {"ok": True, "running": False}
        elif command == "stop" and not running():
            response = {"ok": True, "running": False, "already_stopped": True}
        else:
            response = send({"command": command, **arguments})
    except Exception as error:
        response = {"ok": False, "error": str(error), "type": type(error).__name__}
    print(json.dumps(response, ensure_ascii=False))
    return 0 if response.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
