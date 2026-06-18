"""
ui.py — WebSearch Toggle UI.

ARCHITECTURE:
  LM Studio's built-in chat CANNOT be redirected to a different port.
  It always talks to its own internal server on port 1234.

  The trick:
    1. Change LM Studio's server port to 11435 (in Developer tab)
    2. Our proxy runs on port 1234 (the port LM Studio chat expects)
    3. LM Studio chat \u2192 :1234 (our proxy) \u2192 :11435 (real LM Studio server)
    4. Zero reconfiguration of LM Studio chat needed!

  For Open WebUI users:
    - Keep LM Studio on 1234, proxy on 8000
    - Point Open WebUI to localhost:8000
"""

import tkinter as tk
from tkinter import ttk
import threading
import injector
import detector


_MODES = {
    "lmstudio_direct": {
        "proxy_port": 1234,
        "target_port": 11435,
        "label": "LM Studio Chat (Direct) \u2014 recommended",
    },
    "openwebui": {
        "proxy_port": 8000,
        "target_port": 1234,
        "label": "Open WebUI / External Client",
    },
}


def launch() -> None:
    proxy_started     = False
    clipboard_started = False

    service_info = detector.check_services(verbose=True)

    window = tk.Tk()
    window.title("WebSearch Toggle")
    window.geometry("340x320")
    window.attributes("-topmost", True)
    window.resizable(False, False)

    # Mode selection
    mode_frame = ttk.LabelFrame(window, text="How are you using it?", padding=8)
    mode_frame.pack(fill="x", padx=10, pady=5)

    mode = tk.StringVar(value="lmstudio_direct")

    ttk.Radiobutton(mode_frame,
                    text="LM Studio Chat (Direct)  \u2190 recommended",
                    variable=mode, value="lmstudio_direct").pack(anchor="w")
    ttk.Radiobutton(mode_frame,
                    text="Open WebUI / External Client",
                    variable=mode, value="openwebui").pack(anchor="w")
    ttk.Radiobutton(mode_frame,
                    text="Clipboard (manual copy-paste)",
                    variable=mode, value="clipboard").pack(anchor="w")

    # Toggle button
    toggle_frame = tk.Frame(window)
    toggle_frame.pack(fill="x", padx=10, pady=5)
    toggle_button = tk.Button(
        toggle_frame, text="Web Search: OFF",
        bg="#d9534f", fg="white",
        font=("Helvetica", 11, "bold"),
        relief="flat", padx=10, pady=6,
    )
    toggle_button.pack(fill="x")

    # Status
    svc  = service_info["service"] or "Not detected"
    port = service_info["port"]
    status_label = ttk.Label(window, text=_svc_text(svc, port),
                             font=("Helvetica", 9))
    status_label.pack(pady=2)

    # Instructions box
    info_frame = ttk.LabelFrame(window, text="Setup instructions", padding=6)
    info_frame.pack(fill="x", padx=10, pady=3)
    info_label = ttk.Label(info_frame, text="", foreground="#1a3a6e",
                           wraplength=300,                            font=("Helvetica", 8), justify="left")
    info_label.pack(anchor="w")

    warn_label = ttk.Label(window, text="", foreground="#c0392b",
                           wraplength=320, font=("Helvetica", 8, "bold"))
    warn_label.pack(pady=1)

    def refresh_info(*_):
        m = mode.get()
        svc_detected = bool(service_info.get("port"))

        if m == "lmstudio_direct":
            if not svc_detected:
                info_label.config(text=(
                    "Step 1: LM Studio \u2192 Developer tab\n"
                    "        \u2192 Server Settings \u2192 change port to 11435\n"
                    "        \u2192 click 'Start Server'\n\n"
                    "Step 2: Toggle Web Search ON here\n\n"
                    "Step 3: Chat in LM Studio normally \u2713\n"
                    "        (no other changes needed!)"
                ))
            else:
                info_label.config(text=(
                    "\u2713 LM Studio detected!\n\n"
                    "If using LM Studio chat directly:\n"
                    "  \u2192 Change LM Studio server port to 11435\n"
                    "    (Developer tab \u2192 Server Settings \u2192 Port)\n"
                    "  \u2192 Toggle ON \u2192 Chat normally \u2713\n\n"
                    "Proxy will run on :1234 \u2192 forward to :11435"
                ))

        elif m == "openwebui":
            info_label.config(text=(
                "LM Studio server stays on port 1234.\n\n"
                "Toggle ON \u2192 proxy runs on :8000\n\n"
                "In Open WebUI:\n"
                "  Settings \u2192 change API URL to:\n"
                "  http://localhost:8000\n\n"
                "Chat in Open WebUI \u2192 automatic web search \u2713"
            ))

        else:  # clipboard
            info_label.config(text=(
                "1. Type your question\n"
                "2. Copy it to clipboard (Ctrl+C)\n"
                "3. Press Ctrl+Shift+Enter\n"
                "4. Paste into LM Studio (Ctrl+V)\n\n"
                "Web results are added automatically."
            ))
        warn_label.config(text="")

    mode.trace_add("write", refresh_info)
    refresh_info()

    # Background poll
    def update_status():
        nonlocal service_info
        info = detector.check_services(verbose=False)
        service_info = info
        status_label.config(text=_svc_text(
            info["service"] or "Not detected", info["port"]))
        refresh_info()
        window.after(4000, update_status)

    window.after(4000, update_status)

    all_rbs = mode_frame.winfo_children()

    def toggle_click():
        nonlocal proxy_started, clipboard_started

        currently_on = "ON" in toggle_button["text"]
        turning_on   = not currently_on
        m = mode.get()

        if turning_on:
            cfg = _MODES.get(m)

            if cfg and not service_info.get("port"):
                warn_label.config(
                    text="\u26a0 Start LM Studio server first!\n"
                         "Developer tab \u2192 Server Settings \u2192 Start Server"
                )
                return

            if proxy_started or clipboard_started:
                warn_label.config(text="\u26a0 Already running. Restart app to change mode.")
                return

            toggle_button.config(text="Web Search: ON", bg="#4CAF50")
            warn_label.config(text="")
            injector.set_toggle(True)

            for rb in all_rbs:
                rb.config(state="disabled")

            if m == "lmstudio_direct":
                proxy_started = True
                threading.Thread(
                    target=injector.start_proxy,
                    args=(1234, 11435),
                    daemon=True,
                ).start()
                info_label.config(text=(
                    "\u2713 Proxy running: :1234 \u2192 :11435\n\n"
                    "Make sure LM Studio server is on port 11435\n"
                    "(Developer tab \u2192 Server Settings \u2192 Port: 11435)\n\n"
                    "Chat in LM Studio normally \u2014 web search is automatic! \u2713"
                ))

            elif m == "openwebui":
                proxy_started = True
                threading.Thread(
                    target=injector.start_proxy,
                    args=(8000, service_info["port"]),
                    daemon=True,
                ).start()
                info_label.config(text=(
                    f"\u2713 Proxy running: :8000 \u2192 :{service_info['port']}\n\n"
                    "In Open WebUI \u2192 Settings \u2192 API URL:\n"
                    "  http://localhost:8000\n\n"
                    "Chat in Open WebUI \u2014 web search is automatic! \u2713"
                ))

            elif m == "clipboard":
                clipboard_started = True
                threading.Thread(
                    target=injector.clipboard_mode,
                    daemon=True,
                ).start()

        else:
            toggle_button.config(text="Web Search: OFF", bg="#d9534f")
            injector.set_toggle(False)
            warn_label.config(text="")
            if clipboard_started:
                injector.stop_clipboard_mode()
            refresh_info()

    toggle_button.config(command=toggle_click)

    def on_close():
        injector.set_toggle(False)
        injector.stop_clipboard_mode()
        window.destroy()

    window.protocol("WM_DELETE_WINDOW", on_close)
    window.mainloop()


def _svc_text(svc, port):
    if not port:
        return "\u25cf Service: Not detected \u2014 start LM Studio server!"
    return f"\u25cf Service: {svc.upper()}  port {port}  \u2713"


if __name__ == "__main__":
    launch()
