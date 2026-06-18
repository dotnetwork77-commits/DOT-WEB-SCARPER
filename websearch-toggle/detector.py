"""
detector.py — Detect running local AI services (Ollama, LM Studio).
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
        "port": 1234,
        "probes": [
            "http://localhost:1234/v1/models",
            "http://localhost:1234/api/v0/models",
        ],
    },
]


def check_services(verbose: bool = False) -> dict:
    for entry in _SERVICES:
        for url in entry["probes"]:
            try:
                resp = requests.get(url, timeout=_TIMEOUT)
                if verbose:
                    print(f"\u2713 {entry['service'].capitalize()} detected "
                          f"on port {entry['port']}")
                return {"service": entry["service"], "port": entry["port"]}
            except requests.exceptions.RequestException:
                continue

    if verbose:
        print("\u2717 No AI service detected. Start LM Studio and load a model.")
    return {"service": None, "port": None}


if __name__ == "__main__":
    result = check_services(verbose=True)
    print(result)
