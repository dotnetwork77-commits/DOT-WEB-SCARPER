"""
main.py — Entry point for WebSearch Toggle.

Bug fixed over original:
- Original exited immediately if no AI service was detected at startup.
  This was too aggressive — the user might start Ollama/LM Studio *after*
  launching the toggle. Now we warn but still launch the UI; the UI's
  background status poller will pick up the service once it starts.
"""

import sys
import detector
import ui


def main() -> None:
    print("WebSearch Toggle \u2014 Starting up\u2026")

    service_info = detector.check_services(verbose=True)

    if service_info["service"] is None:
        print()
        print("\u26a0  No AI service detected right now.")
        print("   You can still open the UI \u2014 it will detect the service")
        print("   automatically once Ollama or LM Studio is running.")
        print()
        print("   To start Ollama:    ollama serve")
        print("   To start LM Studio: open LM Studio \u2192 load a model \u2192 start server")
        print()
    else:
        print(f"\u2713 {service_info['service'].upper()} on port {service_info['port']}")
        print()

    print("Launching WebSearch Toggle UI\u2026")
    print("  \u2022 Proxy mode   \u2192 point Open WebUI / AnythingLLM to localhost:8000")
    print("  \u2022 Clipboard mode \u2192 Ctrl+Shift+Enter to inject results")
    print()

    ui.launch()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nWebSearch Toggle stopped.")
    except Exception as exc:
        print(f"\nUnexpected error: {exc}")
        sys.exit(1)
