import json
import os
import subprocess
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from tempfile import TemporaryDirectory


class CliPageHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        body = b"""<!doctype html><title>CLI Test</title>
        <button onclick="this.textContent='Saved'">Save changes</button>
        """
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_args: object) -> None:
        pass


class CliTest(unittest.TestCase):
    def test_session_persists_across_cli_calls(self) -> None:
        with TemporaryDirectory() as state_dir:
            env = {**os.environ, "GLINER_BROWSER_STATE_DIR": state_dir}

            def run(*arguments: str) -> dict:
                completed = subprocess.run(
                    [sys.executable, "-m", "gliner_browser.cli", *arguments],
                    check=True,
                    capture_output=True,
                    text=True,
                    env=env,
                )
                return json.loads(completed.stdout)

            server = ThreadingHTTPServer(("127.0.0.1", 0), CliPageHandler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                self.assertTrue(run("start", "--headless")["ok"])
                self.assertTrue(
                    run("open", f"http://127.0.0.1:{server.server_port}")["ok"]
                )
                observed = run("observe")
                self.assertEqual(observed["elements"][0]["name"], "Save changes")
                self.assertTrue(run("click", observed["elements"][0]["id"])["ok"])
                self.assertEqual(run("observe")["elements"][0]["name"], "Saved")
            finally:
                run("stop")
                server.shutdown()
                server.server_close()


if __name__ == "__main__":
    unittest.main()
