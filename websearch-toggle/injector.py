"""
injector.py — Proxy server and clipboard injection for WebSearch Toggle.

ARCHITECTURE:
  LM Studio's built-in chat cannot be redirected. It always talks to :1234.
  Solution: move LM Studio server to :11435, our proxy runs on :1234.
  Chat -> :1234 (our proxy) -> :11435 (real LM Studio). Zero chat config.

  For Open WebUI: keep LM Studio on :1234, proxy on :8000.
"""

import json
import threading
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler

try:
    import pyperclip
    _PYPERCLIP_OK = True
except ImportError:
    _PYPERCLIP_OK = False

try:
    import keyboard
    _KEYBOARD_OK = True
except ImportError:
    _KEYBOARD_OK = False

_lock = threading.Lock()
_toggle_on = False
_clipboard_stop_event = threading.Event()

_HOP_BY_HOP = {
    "transfer-encoding", "content-encoding", "connection",
    "keep-alive", "proxy-authenticate", "proxy-authorization",
    "te", "trailers", "upgrade",
}

_CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
}


def set_toggle(state: bool) -> None:
    global _toggle_on
    with _lock:
        _toggle_on = state
    print(f"Web Search: {'ON' if state else 'OFF'}")


def get_toggle() -> bool:
    with _lock:
        return _toggle_on


class ProxyHandler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(204)
        for k, v in _CORS_HEADERS.items():
            self.send_header(k, v)
        self.end_headers()

    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)

            try:
                data = json.loads(body.decode("utf-8"))
            except json.JSONDecodeError as exc:
                self._error(400, f"Invalid JSON: {exc}")
                return

            if get_toggle():
                data = _inject_search_results(data)

            new_body = json.dumps(data).encode("utf-8")

            target_port = self.server.target_port
            if not target_port:
                self._error(503, "No AI service port configured.")
                return

            path = self.path or "/v1/chat/completions"
            target_url = f"http://localhost:{target_port}{path}"
            print(f"\u2192 {target_url}")

            upstream = requests.post(
                target_url,
                data=new_body,
                headers={
                    "Content-Type": "application/json",
                    "Content-Length": str(len(new_body)),
                    "User-Agent": "WebSearchToggle/1.0",
                },
                timeout=120,
                stream=True,
            )

            self.send_response(upstream.status_code)
            for key, value in upstream.headers.items():
                if key.lower() not in _HOP_BY_HOP:
                    self.send_header(key, value)
            for k, v in _CORS_HEADERS.items():
                self.send_header(k, v)
            self.end_headers()

            for chunk in upstream.iter_content(chunk_size=4096):
                if chunk:
                    self.wfile.write(chunk)
                    self.wfile.flush()

        except BrokenPipeError:
            pass
        except Exception as exc:
            print(f"Proxy error: {exc}")
            self._error(500, str(exc))

    def do_GET(self):
        try:
            target_port = self.server.target_port
            path = self.path or "/v1/models"
            target_url = f"http://localhost:{target_port}{path}"

            upstream = requests.get(target_url, timeout=10)

            self.send_response(upstream.status_code)
            for key, value in upstream.headers.items():
                if key.lower() not in _HOP_BY_HOP:
                    self.send_header(key, value)
            for k, v in _CORS_HEADERS.items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(upstream.content)
        except Exception as exc:
            self._error(500, str(exc))

    def _error(self, code, message):
        try:
            payload = json.dumps({"error": message}).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            for k, v in _CORS_HEADERS.items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(payload)
        except Exception:
            pass

    def log_message(self, fmt, *args):
        pass


def _inject_search_results(data: dict) -> dict:
    from search import fetch_results
    messages = data.get("messages", [])
    if not messages:
        return data
    for i in range(len(messages) - 1, -1, -1):
        if messages[i].get("role") == "user":
            query = messages[i].get("content", "")
            if not isinstance(query, str):
                break
            print(f"  \u21b3 Searching: {query[:70]}\u2026")
            results = fetch_results(query)
            if results:
                messages[i]["content"] = query + "\n\n" + results
                print("  \u21b3 Injected \u2713")
            else:
                print("  \u21b3 No results.")
            break
    return data


def start_proxy(proxy_port: int, target_port: int) -> None:
    if not target_port:
        print("Proxy not started: target port unknown.")
        return
    server = HTTPServer(("localhost", proxy_port), ProxyHandler)
    server.target_port = target_port
    print(f"Proxy listening on :{proxy_port}  \u2192  :{target_port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def clipboard_mode() -> None:
    if not _PYPERCLIP_OK or not _KEYBOARD_OK:
        print("Clipboard mode unavailable: install pyperclip and keyboard.")
        return
    print("Clipboard mode: Press Ctrl+Shift+Enter to inject search results.")
    _clipboard_stop_event.clear()

    def on_hotkey():
        if not get_toggle():
            print("Web search is OFF.")
            return
        from search import fetch_results
        try:
            text = pyperclip.paste()
            if not text or not text.strip():
                print("Clipboard empty.")
                return
            print(f"Searching: {text[:70]}\u2026")
            results = fetch_results(text)
            if results:
                pyperclip.copy(text + "\n\n" + results)
                print("Done \u2014 paste into LM Studio.")
            else:
                print("No results.")
        except Exception as exc:
            print(f"Clipboard error: {exc}")

    keyboard.add_hotkey("ctrl+shift+enter", on_hotkey)
    _clipboard_stop_event.wait()
    try:
        keyboard.remove_hotkey("ctrl+shift+enter")
    except Exception:
        pass


def stop_clipboard_mode() -> None:
    _clipboard_stop_event.set()
