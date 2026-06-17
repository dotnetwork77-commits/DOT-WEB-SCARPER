# WebSearch Toggle

Gives your local AI model (Ollama / LM Studio) real-time web search capability.  
Free, open source, runs 100% on your computer.

---

## Install

```bash
git clone https://github.com/YOUR_USERNAME/websearch-toggle
cd websearch-toggle
pip install -r requirements.txt
python main.py
```

## Requirements

- Python 3.8 or higher
- Ollama **or** LM Studio installed and running (can be started after the UI opens)

---

## How To Use

1. Run: `python main.py`
2. A small floating window appears
3. Choose your mode (see below)
4. Click **Web Search: OFF** to toggle it ON (green)
5. Start chatting — results are injected automatically

> **Tip:** You can launch the toggle before starting Ollama/LM Studio.  
> The UI detects services in the background every 5 seconds.

---

## Modes

### Proxy Mode — for Open WebUI / AnythingLLM / any OpenAI-compatible client

| Step | What to do |
|------|-----------|
| 1 | Select **Open WebUI / Any LLM** in the toggle window |
| 2 | Click the toggle button to turn Web Search **ON** |
| 3 | In your chat app, set the API base URL to `http://localhost:8000` |
| 4 | Chat normally — search results are silently appended to each prompt |

**How it works:**  
A local HTTP proxy listens on port 8000 and forwards requests to your AI service.  
When the toggle is ON, the last user message is enriched with up to 6 fresh  
DuckDuckGo results (including source URLs) before being forwarded.  
Streaming / SSE responses are passed through chunk-by-chunk so typing  
indicators work correctly.

---

### Clipboard Mode — for LM Studio direct / any chat UI with copy-paste

| Step | What to do |
|------|-----------|
| 1 | Select **LM Studio / Direct** in the toggle window |
| 2 | Click the toggle button to turn Web Search **ON** |
| 3 | Copy your prompt to the clipboard |
| 4 | Press **Ctrl+Shift+Enter** |
| 5 | Paste the enriched prompt into LM Studio (or anywhere else) |

---

## Search Result Format

Results injected into each prompt look like this:

```
[Web Search Results — 2025-06-17]
Query: "latest Python release"

1. Python 3.13 Release Notes
   Python 3.13 was released on October 7 2024…
   Source: https://docs.python.org/3/whatsnew/3.13.html

2. …

Note: Use the above results to inform your answer. Cite sources where relevant.
```

---

## Features

- ✅ Free DuckDuckGo search — no API key needed
- ✅ Auto-detects Ollama and LM Studio (polls every 5 s)
- ✅ Real streaming support — SSE chunks forwarded correctly
- ✅ CORS headers — works with browser-based WebUIs
- ✅ Source URLs in results — model can cite references
- ✅ Smart query cleaning — strips filler words for better retrieval
- ✅ Thread-safe toggle — safe to click rapidly
- ✅ Always-on-top floating window
- ✅ Zero interference when OFF
- ✅ Cross-platform (Windows, Mac, Linux)
- ✅ Open source, MIT License

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "No AI service detected" | Start Ollama (`ollama serve`) or LM Studio, then wait 5 s |
| Proxy returns 502/error | Make sure Ollama/LM Studio is actually running and responding |
| Clipboard mode hotkey not working | Run with `sudo` / admin rights (keyboard library needs it on some OSes) |
| Open WebUI shows CORS error | Update Open WebUI's API URL to `http://localhost:8000` |
| Streaming broken | Make sure you're using the latest version of this file (old version buffered) |

---

## License

MIT License — free for everyone to use, modify, and share.

## Issues

Report issues at: https://github.com/YOUR_USERNAME/websearch-toggle/issues
