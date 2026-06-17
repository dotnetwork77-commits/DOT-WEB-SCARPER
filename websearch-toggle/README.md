# WebSearch Toggle

Gives your local AI model (Ollama / LM Studio) real-time web search capability. Free, open source, runs 100% on your computer.

## Install

```bash
git clone https://github.com/YOUR_USERNAME/websearch-toggle
cd websearch-toggle
pip install -r requirements.txt
python main.py
```

## Requirements

- Python 3.8 or higher
- Ollama OR LM Studio installed and running

## How To Use

1. Start Ollama or LM Studio first
2. Run: `python main.py`
3. A small window appears on your screen
4. Choose your mode:
   - **Open WebUI / AnythingLLM users**: select Proxy Mode, point your app to localhost:8000
   - **LM Studio direct users**: select Clipboard Mode, press Ctrl+Shift+Enter to inject search
5. Toggle Web Search ON or OFF anytime

## Modes Explained

### Proxy Mode (for Open WebUI / AnythingLLM users)
- Runs a local HTTP proxy on port 8000
- Intercepts your chat requests
- When ON: fetches DuckDuckGo results and appends to your prompt
- When OFF: passes requests through unchanged
- Your Open WebUI/AnythingLLM should be configured to use localhost:8000

### Clipboard Mode (for LM Studio direct users)
- Listens for Ctrl+Shift+Enter hotkey
- When pressed: reads your current prompt from clipboard
- When ON: fetches DuckDuckGo results and combines with your prompt
- Copies back to clipboard for you to paste into LM Studio
- Simple and effective for direct LM Studio usage

## Features

- ✅ Free DuckDuckGo search (no API key needed)
- ✅ Auto-detects running AI service
- ✅ Cross-platform (Windows, Mac, Linux)
- ✅ Always-on-top floating window
- ✅ Zero interference when OFF
- ✅ Open source, MIT License

## License

MIT License — free for everyone to use, modify, and share.

## Support

This project is completely free and open source. No ads, no tracking, no hidden costs.

## Issues

Report issues at: https://github.com/YOUR_USERNAME/websearch-toggle/issues