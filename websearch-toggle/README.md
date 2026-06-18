# WebSearch Toggle

Gives your local AI model (Ollama / LM Studio) real-time web search capability.  
Free, open source, runs 100% on your computer.

---

## How It Works

```
LM Studio Chat → :1234 (our proxy adds search results) → :11435 (real LM Studio)
```

LM Studio's chat always talks to port **1234**. We put our proxy in between:
1. Move LM Studio server to port **11435**
2. Our proxy runs on port **1234**
3. Chat sends to 1234 → proxy adds web results → forwards to 11435

**You never need to change anything in LM Studio's chat settings.**

---

## Install

```bash
git clone https://github.com/YOUR_USERNAME/websearch-toggle
cd websearch-toggle
pip install -r requirements.txt
python main.py
```

---

## Step-by-Step Guide

### Step 1: Open LM Studio and load a model
- Open **LM Studio**
- Go to **Chat** tab
- Select a model (e.g., Gemma, Llama, Mistral)
- Wait for **"Model loaded"**

### Step 2: Change the server port to 11435
- Click the **Developer** tab (looks like `</>`)
- Find **Server Settings**
- Change **Port** from `1234` to **`11435`**
- Click **Start Server** (or **Restart Server**)
- Green status appears ✓

### Step 3: Run WebSearch Toggle
- Open **Command Prompt**
- Type:
  ```
  cd C:\Users\neera\DOT-WEB-SCARPER\websearch-toggle
  python main.py
  ```

### Step 4: Start the proxy
- In the toggle window, **"LM Studio Chat (Direct)"** is already selected
- Click the **red button** → turns **green** → says **"Web Search: ON"**
- Proxy is now running: `:1234 → :11435`

### Step 5: Chat normally
- Go to LM Studio **Chat** tab
- Type any question → press **Enter**
- Web search results are automatically added to your question
- The model sees real internet information and answers with it

---

## Other Modes

### Open WebUI / External Client
- Keep LM Studio server on **port 1234** (default)
- In toggle window, select **Open WebUI / External Client**
- Toggle ON → proxy runs on port 8000
- In Open WebUI Settings, set API URL to `http://localhost:8000`
- Chat normally — automatic web search ✓

### Clipboard (Manual)
- Select **Clipboard (manual copy-paste)**
- Toggle ON
- Copy your question (Ctrl+C) → Press **Ctrl+Shift+Enter** → Paste back (Ctrl+V)

---

## Troubleshooting

| Problem | Fix |
|---------|------|
| "LM Studio on port 1234" warning | Change port to **11435** in Developer tab → Server Settings |
| "No AI service detected" | LM Studio Developer tab → Start Server |
| "Connection refused" | Make sure LM Studio server is actually running |
| No web results | Check toggle is ON (green) and internet is connected |
| Port 11435 already in use | Close LM Studio completely, reopen, try again |
| Clipboard hotkey not working | Run Command Prompt as Administrator |

---

## Features

- ✅ Free DuckDuckGo search — no API key needed
- ✅ Works with LM Studio's own chat — zero reconfiguration
- ✅ Proxy intercepts automatically on port 1234
- ✅ Streaming support — responses appear as generated
- ✅ Source URLs in results — model can cite references
- ✅ Clipboard mode for any other app
- ✅ Smart query cleaning — strips filler words
- ✅ Cross-platform (Windows, Mac, Linux)
- ✅ Open source, MIT License
