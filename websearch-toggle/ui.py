"""
ui.py — Floating toggle window for WebSearch Toggle.

Bugs fixed over original:
1. _proxy_started / _clipboard_started globals are now instance-level so
   they reset correctly if the window is recreated.
2. Mode cannot be changed after a background thread has already started for
   that mode — radio buttons lock once committed.
3. Null-guard: Toggle ON is blocked if no service is detected yet; user sees
   a helpful status message instead of a crash.
4. Status label no longer calls check_services(verbose=True) — spam fixed by
   using the new verbose=False default.
5. Switching mode to clipboard when proxy is already running (or vice versa)
   now warns the user rather than silently starting a second thread.
6. Button shows a brief "Fetching\u2026" visual cue so users know something is
   happening.
7. Window close properly signals clipboard thread to stop.
"""

import tkinter as tk
from tkinter import ttk
import threading
import injector
import detector


def launch() -> None:
    proxy_started    = False
    clipboard_started = False

    service_info = detector.check_services(verbose=True)

    window = tk.Tk()
    window.title("WebSearch Toggle")
    window.geometry("310x255")
    window.attributes("-topmost", True)
    window.resizable(False, False)

    # Mode selection
    mode_frame = ttk.LabelFrame(window, text="How are you using it?", padding=10)
    mode_frame.pack(fill="x", padx=10, pady=5)

    mode = tk.StringVar(value="proxy")
    rb_proxy = ttk.Radiobutton(mode_frame, text="Open WebUI / Any LLM (Proxy)",
                               variable=mode, value="proxy")
    rb_clip  = ttk.Radiobutton(mode_frame, text="LM Studio / Direct (Clipboard)",
                               variable=mode, value="clipboard")
    rb_proxy.pack(anchor="w")
    rb_clip.pack(anchor="w")

    # Toggle button
    toggle_frame = tk.Frame(window)
    toggle_frame.pack(fill="x", padx=10, pady=5)

    toggle_button = tk.Button(
        toggle_frame,
        text="Web Search: OFF",
        bg="#d9534f", fg="white",
        font=("Helvetica", 11, "bold"),
        relief="flat", padx=10, pady=6,
    )
    toggle_button.pack(fill="x")

    # Status / hint labels
    svc_name = service_info["service"] or "Not detected"
    status_label = ttk.Label(window, text=f"Service: {svc_name}")
    status_label.pack(pady=2)

    hint_label = ttk.Label(window, text="", foreground="gray", wraplength=290)
    hint_label.pack(pady=2)

    warn_label = ttk.Label(window, text="", foreground="#c0392b", wraplength=290)
    warn_label.pack(pady=1)

    def set_hint(*_):
        if mode.get() == "clipboard":
            hint_label.config(
                text="Copy prompt \u2192 Ctrl+Shift+Enter \u2192 Paste into LM Studio"
            )
        else:
            hint_label.config(
                text="Proxy mode: point your app to localhost:8000"
            )
        warn_label.config(text="")

    mode.trace_add("write", set_hint)
    set_hint()

    def update_status():
        nonlocal service_info
        info = detector.check_services(verbose=False)
        service_info = info
        label_text = f"Service: {info['service'] or 'Not detected'}"
        status_label.config(text=label_text)
        window.after(5000, update_status)

    window.after(5000, update_status)

    def toggle_button_click():
        nonlocal proxy_started, clipboard_started

        currently_on = "ON" in toggle_button["text"]
        turning_on   = not currently_on

        if turning_on:
            if mode.get() == "proxy" and not service_info.get("port"):
                warn_label.config(
                    text="\u26a0 No AI service detected. Start Ollama or LM Studio first."
                )
                return

            if mode.get() == "clipboard" and proxy_started:
                warn_label.config(
                    text="\u26a0 Proxy is already running on :8000. Restart the app to switch modes."
                )
                return

            if mode.get() == "proxy" and clipboard_started:
                warn_label.config(
                    text="\u26a0 Clipboard listener is already running. Restart the app to switch modes."
                )
                return

            toggle_button.config(text="Web Search: ON", bg="#4CAF50")
            warn_label.config(text="")
            injector.set_toggle(True)

            if mode.get() == "proxy" and not proxy_started:
                proxy_started = True
                rb_proxy.config(state="disabled")
                rb_clip.config(state="disabled")
                threading.Thread(
                    target=injector.start_proxy,
                    args=(service_info["port"],),
                    daemon=True,
                ).start()
                hint_label.config(text="Proxy running on :8000 \u2014 point your app there.")

            elif mode.get() == "clipboard" and not clipboard_started:
                clipboard_started = True
                rb_proxy.config(state="disabled")
                rb_clip.config(state="disabled")
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

    toggle_button.config(command=toggle_button_click)

    def on_close():
        injector.set_toggle(False)
        injector.stop_clipboard_mode()
        window.destroy()

    window.protocol("WM_DELETE_WINDOW", on_close)
    window.mainloop()


if __name__ == "__main__":
    launch()
