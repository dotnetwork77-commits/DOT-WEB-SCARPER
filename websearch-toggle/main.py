"""
main.py — Entry point for WebSearch Toggle.
"""

import sys
import detector
import ui


def main() -> None:
    print("WebSearch Toggle \u2014 Starting up\u2026")
    print()

    service_info = detector.check_services(verbose=True)

    if service_info["service"] is None:
        print("\u26a0  No AI service detected.")
        print("   Start LM Studio and load a model first.")
        print()
    else:
        print(f"\u2713 {service_info['service'].upper()} on port {service_info['port']}")
        print()

    print("Launching WebSearch Toggle UI\u2026")
    print()
    ui.launch()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.")
    except Exception as exc:
        print(f"\nError: {exc}")
        sys.exit(1)
