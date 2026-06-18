"""
ui.py — WebSearch Toggle floating window.

IMPORTANT:
  LM Studio's built-in chat talks to the model DIRECTLY — it does NOT
  go through the HTTP server port. A proxy CANNOT intercept its requests.

  Two working approaches:
    1. Clipboard mode — works with ANY app including LM Studio's own chat
       (copy prompt → Ctrl+Shift+Enter → paste back)
    2. Proxy mode — works ONLY with external clients like Open WebUI
       (point their API URL to localhost:8000)
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

    # ── Mode selection ──────────────────────────────────────────────────
    mode_frame = ttk.LabelFrame(window, text="How are you using it?", padding=8)
    mode_frame.pack(fill="x", padx=10, pady=5)
    mode = tk.StringVar(value="clipboard")

    rb1 = ttk.Radiobutton(mode_frame,
                          text="LM Studio Chat (Clipboard)  \u2190 recommended",
                          variable=mode, value="clipboard")
    rb2 = ttk.Radiobutton(mode_frame,
                          text="Open WebUI / External (Proxy)",
                          variable=mode, value="openwebui")
    rb1.pack(anchor="w")
    rb2.pack(anchor="w")
    all_rbs = [rb1, rb2]

    # ── Toggle button ───────────────────────────────────────────────────
    toggle_frame = tk.Frame(window)
    toggle_frame.pack(fill="x", padx=10, pady=5)
    toggle_btn = tk.Button(
        toggle_frame, text="Web Search: OFF",
        bg="#d9534f", fg="white",
        font=("Helvetica", 11, "bold"),
        relief="flat", padx=10, pady=6,
    )
    toggle_btn.pack(fill="x")

    # ── Status ──────────────────────────────────────────────────────────
    status_lbl = ttk.Label(window, font=("Helvetica", 9))
    status_lbl.pack(pady=2)

    # ── Info box ────────────────────────────────────────────────────────
    info_frame = ttk.LabelFrame(window, text="How to use", padding=6)
    info_frame.pack(fill="x", padx=10, pady=3)
    info_lbl = ttk.Label(info_frame, text="",
                         foreground="#1a3a6e", wraplength=305,
                         font=("Helvetica", 8), justify="left")
    info_lbl.pack(anchor="w")

    warn_lbl = ttk.Label(window, text="", foreground="#c0392b",
                         wraplength=320, font=("Helvetica", 8, "bold"))
    warn_lbl.pack(pady=1)

    # ── Helpers ─────────────────────────────────────────────────────────
    def refresh_status():
        svc  = service_info.get("service") or "Not detected"
        port = service_info.get("port")
        if port:
            status_lbl.config(
                text=f"\u25cf {svc.upper()} detected on port {port}",
                foreground="#1a6e2e"
            )
        else:
            status_lbl.config(
                text="\u25cf LM Studio not detected \u2014 start it first",
                foreground="#c0392b"
            )

    def refresh_info(*_):
        m = mode.get()
        warn_lbl.config(text="")

        if m == "clipboard":
            info_lbl.config(text=(
                "Clipboard mode works with every app.\n\n"
                "1. Type your question in LM Studio\n"
                "2. Copy it (Ctrl+A then Ctrl+C)\n"
                "3. Press Ctrl+Shift+Enter\n"
                "4. Paste back (Ctrl+A then Ctrl+V)\n"
                "5. Press Enter to send\n\n"
                "The web results are added to your prompt. \u2713"
            ))
        else:
            port = service_info.get("port") or 1234
            info_lbl.config(text=(
                "Proxy mode \u2014 for Open WebUI / external apps only.\n\n"
                "Toggle ON \u2192 proxy runs on :8000\n\n"
                "In Open WebUI Settings, set API URL to:\n"
                "  http://localhost:8000\n\n"
                "Chat in Open WebUI \u2014 automatic web search \u2713\n\n"
                "(Keep LM Studio server on port 1234)"
            ))

    mode.trace_add("write", refresh_info)
    refresh_status()
    refresh_info()

    # ── Background poll ─────────────────────────────────────────────────
    def poll():
        nonlocal service_info
        info = detector.check_services(verbose=False)
        service_info = info
        refresh_status()
        window.after(4000, poll)

    window.after(4000, poll)

    # ── Toggle logic ────────────────────────────────────────────────────
    def toggle_click():
        nonlocal proxy_started, clipboard_started

        currently_on = "ON" in toggle_btn["text"]
        turning_on   = not currently_on
        m = mode.get()

        if turning_on:
            # First-time startup
            if not proxy_started and not clipboard_started:
                if m == "openwebui" and not service_info.get("port"):
                    warn_lbl.config(
                        text="\u26a0 LM Studio not detected. Start it first."
                    )
                    return

                for rb in all_rbs:
                    rb.config(state="disabled")

                if m == "openwebui":
                    proxy_started = True
                    threading.Thread(
                        target=injector.start_proxy,
                        args=(8000, service_info["port"]),
                        daemon=True,
                    ).start()
                else:
                    clipboard_started = True
                    threading.Thread(
                        target=injector.clipboard_mode,
                        daemon=True,
                    ).start()

            # Re-enable injection
            toggle_btn.config(text="Web Search: ON", bg="#4CAF50")
            warn_lbl.config(text="")
            injector.set_toggle(True)

            if m == "openwebui":
                info_lbl.config(text=(
                    f"\u2713 Proxy on :8000 \u2192 :{service_info['port']}\n\n"
                    "Open WebUI \u2192 API URL:\n"
                    "  http://localhost:8000"
                ))

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
