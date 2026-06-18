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
        print()
        print("\u26a0  No AI service detected.")
        print("   The UI will auto-detect once LM Studio is running.")
        print()
        print("   LM Studio setup:")
        print("   1. Open LM Studio \u2192 Developer tab")
        print("   2. Server Settings \u2192 change Port to 11435")
        print("   3. Click 'Start Server'")
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
