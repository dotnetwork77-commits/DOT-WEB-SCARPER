import detector
import ui
import injector
import sys

def main():
    """Main entry point for WebSearch Toggle."""
    print("WebSearch Toggle - Starting up...")
    
    # Check for running services
    service_info = detector.check_services()
    
    if service_info['service'] is None:
        print("\n❌ No AI service detected!")
        print("Please start Ollama or LM Studio first.")
        print("\nTo install and run Ollama:")
        print("1. Download from https://ollama.ai/")
        print("2. Run: ollama serve")
        print("\nTo install and run LM Studio:")
        print("1. Download from https://lmstudio.ai/")
        print("2. Start LM Studio and load a model")
        sys.exit(1)
    
    print(f"✓ {service_info['service'].upper()} detected on port {service_info['port']}")
    print("\nLaunching WebSearch Toggle UI...")
    print("Choose your mode in the window:")
    print("  - Open WebUI / Any LLM → Proxy Mode")
    print("  - LM Studio / Direct → Clipboard Mode")
    print("\nToggle Web Search ON/OFF as needed")
    print("For Clipboard Mode: Press Ctrl+Shift+Enter to inject")
    
    # Launch the UI
    ui.launch()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nWebSearch Toggle stopped.")
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)