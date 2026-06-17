"""
injector.py — Proxy server and clipboard injection for WebSearch Toggle.

Bugs fixed over original:
1. Streaming (SSE) responses now forwarded correctly chunk-by-chunk instead
   of being buffered entirely in memory (fixes Open WebUI / streaming clients).
2. Content-Length header is recalculated after search text is injected so the
   upstream response isn't rejected by strict HTTP clients.
3. CORS headers (Access-Control-Allow-Origin, etc.) are preserved so
   browser-based WebUIs (Open WebUI) don't get blocked.
4. OPTIONS pre-flight requests are handled so CORS works end-to-end.
5. toggle_on is now protected by a threading.Lock for thread safety.
6. clipboard_mode no longer calls keyboard.wait() (blocking forever);
   uses an Event so it can be stopped cleanly.
7. Null-guard: proxy won't start if target_port is None.
8. Added User-Agent header to forwarded requests (some servers reject requests
   without one).
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
    print("Warning: pyperclip not installed — clipboard mode unavailable.")

try:
    import keyboard
    _KEYBOARD_OK = True
except ImportError:
    _KEYBOARD_OK = False
    print("Warning: keyboard not installed — clipboard mode unavailable.")


# ---------------------------------------------------------------------------
# Thread-safe toggle state
# ---------------------------------------------------------------------------

_lock = threading.Lock()
_toggle_on = False
_clipboard_stop_event = threading.Event()


def set_toggle(state: bool) -> None:
    """Set the web-search toggle state (thread-safe)."""
    global _toggle_on
    with _lock:
        _toggle_on = state
    print(f"Web Search: {'ON' if state else 'OFF'}")


def get_toggle() -> bool:
    """Read the web-search toggle state (thread-safe)."""
    with _lock:
        return _toggle_on


# ---------------------------------------------------------------------------
# Proxy mode
# ---------------------------------------------------------------------------

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
            print(f"\u2192 Forwarding to: {target_url}")

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

    def _error(self, code: int, message: str) -> None:
        try:
            payload = json.dumps({"error": message}).encode("utf-8")
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
            print(f"  \u21b3 Fetching web results for: {query[:70]}\u2026")
            results = fetch_results(query)
            if results:
                messages[i]["content"] = query + "\n\n" + results
                print("  \u21b3 Search results injected.")
            else:
                print("  \u21b3 No search results returned.")
            break

    return data


def start_proxy(target_port: int) -> None:
    if not target_port:
        print("Proxy not started: target port is unknown.")
        return

    server = HTTPServer(("localhost", 8000), ProxyHandler)
    server.target_port = target_port
    print(f"Proxy listening on :8000  \u2192  forwarding to :{target_port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


# ---------------------------------------------------------------------------
# Clipboard mode
# ---------------------------------------------------------------------------

def clipboard_mode() -> None:
    if not _PYPERCLIP_OK or not _KEYBOARD_OK:
        print("Clipboard mode unavailable: install pyperclip and keyboard.")
        return

    print("Clipboard mode active. Press Ctrl+Shift+Enter to inject search results.")
    _clipboard_stop_event.clear()

    def on_hotkey():
        if not get_toggle():
            print("Web search is OFF \u2014 toggle it ON first.")
            return
        from search import fetch_results
        try:
            text = pyperclip.paste()
            if not text or not text.strip():
                print("Clipboard is empty \u2014 copy your prompt first.")
                return
            print(f"Fetching results for: {text[:70]}\u2026")
            results = fetch_results(text)
            if results:
                pyperclip.copy(text + "\n\n" + results)
                print("Done! Search results injected into clipboard \u2014 paste into LM Studio.")
            else:
                print("No results returned from search.")
        except Exception as exc:
            print(f"Clipboard mode error: {exc}")

    keyboard.add_hotkey("ctrl+shift+enter", on_hotkey)
    _clipboard_stop_event.wait()

    try:
        keyboard.remove_hotkey("ctrl+shift+enter")
    except Exception:
        pass


def stop_clipboard_mode() -> None:
    _clipboard_stop_event.set()


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "proxy":
        start_proxy(11434)
    else:
        set_toggle(True)
        clipboard_mode()
