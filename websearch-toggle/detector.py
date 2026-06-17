import requests

def check_services():
    """Check if Ollama or LM Studio is running and return service info."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✓ Ollama service detected on port 11434")
            return {'service': 'ollama', 'port': 11434}
    except requests.exceptions.RequestException:
        pass

    try:
        response = requests.get("http://localhost:1234/v1/models", timeout=5)
        if response.status_code == 200:
            print("✓ LM Studio service detected on port 1234")
            return {'service': 'lmstudio', 'port': 1234}
    except requests.exceptions.RequestException:
        pass

    print("✗ No AI service detected. Please start Ollama or LM Studio first.")
    return {'service': None, 'port': None}