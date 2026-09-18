import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory

from gliner_browser.runtime import BrowserRuntime


class PageHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        body = b"""<!doctype html><title>Test</title>
        <button onclick="document.body.dataset.clicked='yes'">Save changes</button>
        <input aria-label="Email address">
        """
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_args: object) -> None:
        pass


class BrowserRuntimeTest(unittest.TestCase):
    def test_observes_and_clicks_an_explicit_element(self) -> None:
        server = ThreadingHTTPServer(("127.0.0.1", 0), PageHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with TemporaryDirectory() as profile:
                runtime = BrowserRuntime(Path(profile), headless=True)
                try:
                    runtime.open(f"http://127.0.0.1:{server.server_port}")
                    elements = runtime.observe()["elements"]
                    save = next(item for item in elements if item["name"] == "Save changes")
                    runtime.click(save["id"])
                    self.assertEqual(
                        runtime.page.locator("body").get_attribute("data-clicked"), "yes"
                    )
                finally:
                    runtime.close()
        finally:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    unittest.main()
