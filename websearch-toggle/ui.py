"""
ui.py — WebSearch Toggle floating window.

Three modes:
  1. LM Studio Direct  — proxy on :1234, LM Studio server on :11435
  2. Open WebUI        — proxy on :8000, LM Studio server on :1234
  3. Clipboard         — manual Ctrl+Shift+Enter inject
"""

import tkinter as tk
from tkinter import ttk
import threading
import injector
import detector


def launch() -> None:
    proxy_started     = False
    clipboard_started = False
    service_info      = detector.check_services(verbose=True)

    window = tk.Tk()
    window.title("WebSearch Toggle")
    window.geometry("340x330")
    window.attributes("-topmost", True)
    window.resizable(False, False)

    # Mode selection
    mode_frame = ttk.LabelFrame(window, text="How are you using it?", padding=8)
    mode_frame.pack(fill="x", padx=10, pady=5)
    mode = tk.StringVar(value="lmstudio_direct")

    rb1 = ttk.Radiobutton(mode_frame,
                          text="LM Studio Chat (Direct)  \u2190 recommended",
                          variable=mode, value="lmstudio_direct")
    rb2 = ttk.Radiobutton(mode_frame,
                          text="Open WebUI / External Client",
                          variable=mode, value="openwebui")
    rb3 = ttk.Radiobutton(mode_frame,
                          text="Clipboard (manual copy-paste)",
                          variable=mode, value="clipboard")
    rb1.pack(anchor="w")
    rb2.pack(anchor="w")
    rb3.pack(anchor="w")
    all_rbs = [rb1, rb2, rb3]

    # Toggle button
    toggle_frame = tk.Frame(window)
    toggle_frame.pack(fill="x", padx=10, pady=5)
    toggle_btn = tk.Button(
        toggle_frame, text="Web Search: OFF",
        bg="#d9534f", fg="white",
        font=("Helvetica", 11, "bold"),
        relief="flat", padx=10, pady=6,
    )
    toggle_btn.pack(fill="x")

    # Status
    status_lbl = ttk.Label(window, font=("Helvetica", 9))
    status_lbl.pack(pady=2)

    # Info box
    info_frame = ttk.LabelFrame(window, text="Setup", padding=6)
    info_frame.pack(fill="x", padx=10, pady=3)
    info_lbl = ttk.Label(info_frame, text="",
                         foreground="#1a3a6e", wraplength=305,
                         font=("Helvetica", 8), justify="left")
    info_lbl.pack(anchor="w")

    warn_lbl = ttk.Label(window, text="", foreground="#c0392b",
                         wraplength=320, font=("Helvetica", 8, "bold"))
    warn_lbl.pack(pady=1)

    def refresh_status():
        svc  = service_info.get("service") or "Not detected"
        port = service_info.get("port")
        if port:
            status_lbl.config(
                text=f"\u25cf {svc.upper()} on port {port}  \u2713",
                foreground="#1a6e2e"
            )
        else:
            status_lbl.config(
                text="\u25cf Service: Not detected \u2014 start LM Studio server!",
                foreground="#c0392b"
            )

    def refresh_info(*_):
        m    = mode.get()
        port = service_info.get("port")
        warn_lbl.config(text="")

        if m == "lmstudio_direct":
            if port == 11435:
                info_lbl.config(text=(
                    "\u2713 LM Studio running on port 11435\n\n"
                    "Toggle ON \u2192 proxy intercepts :1234 \u2192 :11435\n"
                    "Chat in LM Studio normally \u2014 automatic! \u2713"
                ))
            elif port == 1234:
                info_lbl.config(text=(
                    "\u26a0 LM Studio is on port 1234 (default).\n\n"
                    "Please change it to 11435:\n"
                    "  LM Studio \u2192 Developer tab\n"
                    "  \u2192 Server Settings \u2192 Port: 11435\n"
                    "  \u2192 Stop Server \u2192 Start Server\n\n"
                    "Then toggle ON here."
                ))
            else:
                info_lbl.config(text=(
                    "LM Studio server not detected.\n\n"
                    "  LM Studio \u2192 Developer tab\n"
                    "  \u2192 Server Settings \u2192 Port: 11435\n"
                    "  \u2192 click 'Start Server'\n\n"
                    "Then toggle ON here."
                ))

        elif m == "openwebui":
            info_lbl.config(text=(
                "LM Studio server stays on port 1234.\n\n"
                "Toggle ON \u2192 proxy runs on :8000\n\n"
                "In Open WebUI \u2192 Settings \u2192 API URL:\n"
                "  http://localhost:8000\n\n"
                "Chat in Open WebUI \u2192 automatic \u2713"
            ))

        else:
            info_lbl.config(text=(
                "1. Copy your question (Ctrl+C)\n"
                "2. Press Ctrl+Shift+Enter\n"
                "3. Paste into LM Studio (Ctrl+V)\n\n"
                "Web results are added automatically."
            ))

    mode.trace_add("write", refresh_info)
    refresh_status()
    refresh_info()

    def poll():
        nonlocal service_info
        info = detector.check_services(verbose=False)
        service_info = info
        refresh_status()
        refresh_info()
        window.after(4000, poll)

    window.after(4000, poll)

    def toggle_click():
        nonlocal proxy_started, clipboard_started

        currently_on = "ON" in toggle_btn["text"]
        turning_on   = not currently_on
        m = mode.get()

        if turning_on:
            if m in ("lmstudio_direct", "openwebui"):
                port = service_info.get("port")
                if not port:
                    warn_lbl.config(
                        text="\u26a0 Start LM Studio server first!\n"
                             "Developer tab \u2192 Port 11435 \u2192 Start Server"
                    )
                    return
                if m == "lmstudio_direct" and port != 11435:
                    warn_lbl.config(
                        text="\u26a0 Change LM Studio server port to 11435 first!\n"
                             "Developer tab \u2192 Server Settings \u2192 Port: 11435\n"
                             "\u2192 Stop & Start Server"
                    )
                    return

            if proxy_started or clipboard_started:
                warn_lbl.config(text="\u26a0 Already running. Restart app to change mode.")
                return

            toggle_btn.config(text="Web Search: ON", bg="#4CAF50")
            warn_lbl.config(text="")
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
                info_lbl.config(text=(
                    "\u2713 Proxy running: :1234 \u2192 :11435\n\n"
                    "Just chat in LM Studio normally.\n"
                    "Every message gets live web results. \u2713"
                ))

            elif m == "openwebui":
                proxy_started = True
                threading.Thread(
                    target=injector.start_proxy,
                    args=(8000, service_info["port"]),
                    daemon=True,
                ).start()
                info_lbl.config(text=(
                    f"\u2713 Proxy: :8000 \u2192 :{service_info['port']}\n\n"
                    "Open WebUI \u2192 Settings \u2192 API URL:\n"
                    "  http://localhost:8000\n\n"
                    "Chat in Open WebUI \u2014 automatic \u2713"
                ))

            elif m == "clipboard":
                clipboard_started = True
                threading.Thread(
                    target=injector.clipboard_mode,
                    daemon=True,
                ).start()

        else:
            toggle_btn.config(text="Web Search: OFF", bg="#d9534f")
            injector.set_toggle(False)
            if clipboard_started:
                injector.stop_clipboard_mode()
            refresh_info()

    toggle_btn.config(command=toggle_click)

    def on_close():
        injector.set_toggle(False)
        injector.stop_clipboard_mode()
        window.destroy()

    window.protocol("WM_DELETE_WINDOW", on_close)
    window.mainloop()


if __name__ == "__main__":
    launch()
