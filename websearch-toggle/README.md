# WebSearch Toggle

Gives your local AI model (Ollama / LM Studio) real-time web search capability.  
Free, open source, runs 100% on your computer.

---

## How It Works

```
LM Studio Chat → :1234 (our proxy adds search results) → :11435 (real LM Studio)
```

LM Studio's chat always talks to port 1234. We put our proxy **in between**:
1. Move LM Studio server to port **11435**
2. Our proxy runs on **port 1234** (the chat's default target)
3. Chat sends to 1234 → proxy adds web results → forwards to 11435

**Zero chat reconfiguration needed.**

---

## Install

```bash
git clone https://github.com/YOUR_USERNAME/websearch-toggle
cd websearch-toggle
pip install -r requirements.txt
python main.py
```

---

## Step-by-Step Guide (LM Studio Direct — Recommended)

### Step 1: Load a model in LM Studio
- Open LM Studio
- Go to **Chat** tab
- Select a model from the dropdown (e.g., Gemma, Llama)
- Wait until it says **"Model loaded"**

### Step 2: Change LM Studio's server port to 11435
- Click the **Developer** tab (looks like `</>`)
- Find **Server Settings** section
- Change the **Port** field from `1234` to **`11435`**
- Click **Start Server** (or **Restart Server**)
- You should see a green status indicator

### Step 3: Run WebSearch Toggle
- Open **Command Prompt** (or Terminal)
- Type: `cd C:\Users\neera\DOT-WEB-SCARPER\websearch-toggle`
- Type: `python main.py`
- A small window will appear

### Step 4: Start the proxy
- The window shows **"LM Studio Chat (Direct)"** is selected
- Click the **red button** → it turns **green** and says **"Web Search: ON"**
- The proxy is now running on port 1234, forwarding to LM Studio on 11435

### Step 5: Chat normally
- Go to LM Studio **Chat** tab
- Type any question and press **Enter**
- Web search results are automatically added to your question
- The model sees the search results and answers with real information

---

## Other Modes

### Copy-Paste Mode (Clipboard)
For when you can't change the server port.

1. In the toggle window, select **Clipboard (manual copy-paste)**
2. Click toggle ON (green)
3. Type question in LM Studio → **Copy** (Ctrl+C)
4. Press **Ctrl+Shift+Enter**
5. **Paste** back into LM Studio (Ctrl+V) → press Enter

### Open WebUI / External Client
For users of Open WebUI, AnythingLLM, etc.

1. In the toggle window, select **Open WebUI / External Client**
2. **Keep** LM Studio server on port 1234 (default)
3. Click toggle ON (green) — proxy runs on port 8000
4. In Open WebUI Settings → change API URL to `http://localhost:8000`
5. Chat normally — automatic web search

---

## Search Result Format

Results look like this inside your prompt:

```
[Web Search Results — 2025-06-17]
Query: "capital of France"

1. Paris - Wikipedia
   Paris is the capital and largest city of France...
   Source: https://en.wikipedia.org/wiki/Paris

Note: Use the above results to inform your answer. Cite sources where relevant.
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "Connection refused" | Make sure LM Studio Developer tab → Start Server is running |
| No web results in answer | Check toggle is **ON** (green). Check internet connection. |
| LM Studio can't start on 11435 | Port already in use. Restart LM Studio completely. |
| Clipboard hotkey not working | Run Command Prompt as Administrator |
| Proxy already running | Close the toggle window and reopen |

---

## Features

- ✅ Free DuckDuckGo search — no API key needed
- ✅ Works with LM Studio's own chat — no extra apps needed
- ✅ Zero chat reconfiguration — proxy intercepts automatically
- ✅ Streaming support — responses appear as they're generated
- ✅ Source URLs in results — model can cite references
- ✅ Clipboard mode for any other app
- ✅ Always-on-top floating window
- ✅ Cross-platform (Windows, Mac, Linux)
- ✅ Open source, MIT License
