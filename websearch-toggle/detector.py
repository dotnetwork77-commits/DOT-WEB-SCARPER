"""
detector.py — Detect Ollama / LM Studio on all known ports.
Checks port 11435 first (our moved LM Studio port), then 1234 (default).
"""

import requests

_TIMEOUT = 1.5

_SERVICES = [
    {
        "service": "ollama",
        "port": 11434,
        "probes": [
            "http://localhost:11434/api/tags",
            "http://localhost:11434/api/version",
        ],
    },
    {
        "service": "lmstudio",
        "port": 11435,
        "probes": [
            "http://localhost:11435/v1/models",
            "http://localhost:11435/api/v0/models",
            "http://localhost:11435/api/v1/models",
        ],
    },
    {
        "service": "lmstudio",
        "port": 1234,
        "probes": [
            "http://localhost:1234/v1/models",
            "http://localhost:1234/api/v0/models",
            "http://localhost:1234/api/v1/models",
        ],
    },
]


def check_services(verbose: bool = False) -> dict:
    """
    Probe all known ports. Returns first one that responds.
    Never probes port 8000 (that's our own proxy).
    """
    for entry in _SERVICES:
        for url in entry["probes"]:
            try:
                resp = requests.get(url, timeout=_TIMEOUT)
                if verbose:
                    print(f"\u2713 {entry['service'].capitalize()} detected "
                          f"on port {entry['port']} (HTTP {resp.status_code})")
                return {"service": entry["service"], "port": entry["port"]}
            except requests.exceptions.ConnectionError:
                continue
            except requests.exceptions.Timeout:
                continue
            except Exception:
                continue

    if verbose:
        print("\u2717 No AI service detected.")
        print("  \u2192 LM Studio: Developer tab \u2192 Server Settings \u2192 Port: 11435 \u2192 Start Server")
    return {"service": None, "port": None}


if __name__ == "__main__":
    result = check_services(verbose=True)
    print(result)
