"""
detector.py — Detect running local AI services (Ollama, LM Studio).

Bugs fixed over original:
1. Polling no longer prints to stdout every 5 seconds — the UI was being
   spammed with "✓ Ollama detected" on every status refresh.
   Verbose logging is now opt-in via the `verbose` parameter.
2. Connection timeout reduced from 5 s to 2 s so startup isn't sluggish.
3. Added LM Studio's alternative /v1/chat/completions probe in case
   /v1/models returns 404 on older builds.
4. Returns port in the dict even for LM Studio so proxy mode works correctly.
"""

import requests


# ---------------------------------------------------------------------------
# Service definitions
# Probe each URL; the first one that responds 200 wins.
# ---------------------------------------------------------------------------

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
            "http://localhost:1234/v1/chat/completions",
        ],
    },
]

_TIMEOUT = 2.0


def check_services(verbose: bool = False) -> dict:
    """
    Probe localhost for a running Ollama or LM Studio service.

    Args:
        verbose: If True, print detection status to stdout.
                 Pass False (default) for silent background polling.

    Returns:
        {'service': 'ollama'|'lmstudio'|None, 'port': int|None}
    """
    for entry in _SERVICES:
        for url in entry["probes"]:
            try:
                resp = requests.get(url, timeout=_TIMEOUT)
                if resp.status_code == 200:
                    if verbose:
                        print(f"✓ {entry['service'].capitalize()} service detected "
                              f"on port {entry['port']}")
                    return {"service": entry["service"], "port": entry["port"]}
            except requests.exceptions.RequestException:
                continue

    if verbose:
        print("✗ No AI service detected. Please start Ollama or LM Studio first.")
    return {"service": None, "port": None}


if __name__ == "__main__":
    result = check_services(verbose=True)
    print(result)
