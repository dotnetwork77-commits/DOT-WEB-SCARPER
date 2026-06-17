import json
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
import pyperclip
import keyboard

# Global toggle state
toggle_on = False

def set_toggle(state):
    """Set the toggle state."""
    global toggle_on
    toggle_on = state
    print(f"Web Search: {'ON' if toggle_on else 'OFF'}")

class ProxyHandler(BaseHTTPRequestHandler):
    """HTTP request handler for proxy mode."""
    
    def do_POST(self):
        """Handle POST requests in proxy mode."""
        try:
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            
            if toggle_on:
                from search import fetch_results
                data = json.loads(body.decode('utf-8'))
                
                if data.get('messages') and len(data['messages']) > 0:
                    last_message = data['messages'][-1]
                    if last_message.get('role') == 'user':
                        query = last_message.get('content', '')
                        results = fetch_results(query)
                        if results:
                            last_message['content'] += '\n\n' + results
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            target_port = 11434 if self.server.target_port == 11434 else 1234
            requests.post(f"http://localhost:{target_port}", 
                         json=json.loads(body.decode('utf-8')), 
                         timeout=30)
                         
        except Exception as e:
            print(f"Proxy error: {e}")
            self.send_response(500)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress log messages."""
        pass

def start_proxy(target_port):
    """Start the HTTP proxy server."""
    server = HTTPServer(('localhost', 8000), ProxyHandler)
    server.target_port = target_port
    print(f"Proxy server started on port 8000 (forwarding to port {target_port})")
    server.serve_forever()

def clipboard_mode():
    """Listen for Ctrl+Shift+Enter hotkey and inject search results."""
    print("Clipboard mode active. Press Ctrl+Shift+Enter to inject search results.")
    
    def on_hotkey():
        global toggle_on
        if toggle_on:
            from search import fetch_results
            try:
                text = pyperclip.paste()
                if text:
                    results = fetch_results(text)
                    if results:
                        combined = text + '\n\n' + results
                        pyperclip.copy(combined)
                        print("Search results injected into clipboard!")
            except Exception as e:
                print(f"Clipboard mode error: {e}")
    
    keyboard.add_hotkey('ctrl+shift+enter', on_hotkey)
    keyboard.wait()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "proxy":
        start_proxy(11434)
    else:
        clipboard_mode()