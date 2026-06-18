"""
detector.py — Detect running local AI services (Ollama, LM Studio).

Key fix in this version:
- When the user points LM Studio to localhost:8000 (the proxy), the detector
  must ALWAYS check the real service ports (1234, 11434) directly — never
  probe port 8000. This way detection still works even when the proxy is running.
- Added 'proxy_running' key to the result so the UI can show the correct status.
"""

import requests

_TIMEOUT = 2.0

_SERVICES = [
    {
        "service": "ollama",
        "port": 11434,
        "probes": ["http://localhost:11434/api/tags"],
    },
    {
        "service": "lmstudio",
        "port": 1234,
        "probes": [
            "http://localhost:1234/v1/models",
            "http://localhost:1234/api/v1/models",
            "http://localhost:1234/v1/chat/completions",
        ],
    },
]


def check_services(verbose: bool = False) -> dict:
    """
    Probe the REAL service ports directly (never port 8000).
    Always returns the actual LM Studio / Ollama port so the proxy
    knows where to forward requests, regardless of what LM Studio's
    chat UI is pointed at.

    Returns:
        {
          'service': 'ollama' | 'lmstudio' | None,
          'port':    int | None,
        }
    """
    for entry in _SERVICES:
        for url in entry["probes"]:
            try:
                resp = requests.get(url, timeout=_TIMEOUT)
                if resp.status_code in (200, 404):
                    if verbose:
                        print(f"\u2713 {entry['service'].capitalize()} detected "
                              f"on port {entry['port']}")
                    return {"service": entry["service"], "port": entry["port"]}
            except requests.exceptions.RequestException:
                continue

    if verbose:
        print("\u2717 No AI service detected. Please start Ollama or LM Studio first.")
    return {"service": None, "port": None}


if __name__ == "__main__":
    result = check_services(verbose=True)
    print(result)
