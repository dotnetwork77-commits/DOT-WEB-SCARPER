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
- Ollama **or** LM Studio installed and running

---

## How To Use — Step by Step

### Step 1: Open LM Studio and load a model

1. Open **LM Studio**
2. Click the **Search** tab on the left
3. Search for a model (e.g., `gemma`, `llama`, `mistral`)
4. Click **Download** on the model you want
5. Once downloaded, click the **Chat** tab on the left
6. Select your model from the dropdown at the top
7. Wait for it to load (you'll see "Model loaded" message)

### Step 2: Start the LM Studio server

1. Click the **Developer** tab on the left (looks like `</>`)
2. You'll see a **Start Server** button — click it
3. The button will change to **Stop Server** and show a green status
4. Note the **Port** number (default is `1234`) — don't change it yet

### Step 3: Run WebSearch Toggle

1. Open **Command Prompt** or **Terminal**
2. Type this command and press Enter:
   ```
   cd C:\Users\neera\DOT-WEB-SCARPER\websearch-toggle
   python main.py
   ```
3. A small floating window will appear titled **"WebSearch Toggle"**

### Step 4: Configure the toggle

1. In the popup window, the top option **"LM Studio / Open WebUI (Proxy)"** should be selected (this is the recommended mode)
2. The status line should show: `Service: lmstudio (real port: 1234)`
3. Click the **red button** that says **"Web Search: OFF"** — it turns **green** and says **"Web Search: ON"**
4. The hint will update to show a message about pointing LM Studio to localhost:8000

### Step 5: Change LM Studio's port to 8000

This is the most important step. The WebSearch Toggle runs a proxy on port 8000 that adds search results to your questions. You need to tell LM Studio to send requests to port 8000 instead of port 1234.

1. Go back to LM Studio's **Developer** tab
2. Find the **Port** field (it says `1234`)
3. **Change it to `8000`**
4. Click **Restart Server** (the Start Server button again)
5. You'll see the green status reappear — now LM Studio's chat will send requests to the WebSearch Toggle proxy

### Step 6: Chat normally

1. Go to the **Chat** tab in LM Studio
2. Type any question in the chat box, for example: `What is the capital of France?`
3. Press **Enter**
4. The toggle proxy will automatically:
   - Take your question
   - Search the internet for answers
   - Add the search results to your question
   - Forward it to Gemma/Llama in LM Studio
5. Gemma will respond with an answer that includes web search information

---

## How It Works

```
You type a question → WebSearch Toggle (port 8000) adds search results
         → Forwards to LM Studio (port 1234) → Gemma answers
```

The toggle acts as a **middleman**. Your question goes to port 8000 first, where web search results are attached, then it's sent to LM Studio's real port (1234). This all happens automatically in the background.

---

## Modes

### Proxy Mode (Recommended) — Works with LM Studio's own chat

**Best for:** Most users. No copy-paste needed. Just type and send.

| Step | Action |
|------|--------|
| 1 | Select **LM Studio / Open WebUI (Proxy)** in the toggle window |
| 2 | Click toggle to turn it **ON** (green) |
| 3 | In LM Studio Developer tab, change port to **8000**, restart server |
| 4 | Type any question in LM Studio Chat and press Enter |
| 5 | Web results are added automatically — no extra steps |

### Clipboard Mode — Works with any app

**Best for:** When you can't change the server port.

| Step | Action |
|------|--------|
| 1 | Select **LM Studio Direct (Clipboard)** |
| 2 | Click toggle to turn it **ON** (green) |
| 3 | Type your question in LM Studio and **copy it** (Ctrl+C) |
| 4 | Press **Ctrl+Shift+Enter** |
| 5 | Go back to LM Studio, **paste** (Ctrl+V), press Enter |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| **"No AI service detected"** | Make sure LM Studio is running and a model is loaded. Wait 5 seconds for the auto-detect. |
| **LM Studio says "Connection refused"** | You changed the port to 8000 but the toggle isn't running. Run `python main.py` and turn the toggle ON first. |
| **Gemma says "I can't access the internet"** | The search results are added to the question itself, not to Gemma. Gemma reads the search results from your question text. If you see "Web Search Results" in your question after sending, it's working. |
| **Toggle button is disabled** | Click it to turn it ON (green). If it's red and says OFF, click it. |
| **Clipboard mode hotkey not working** | Run Command Prompt as **Administrator** (right-click → Run as Administrator), then run `python main.py` again. |
| **No search results appearing** | Check your internet connection. DuckDuckGo requires internet access. |

---

## Features

- ✅ Free DuckDuckGo search — no API key needed
- ✅ Auto-detects Ollama and LM Studio
- ✅ Proxy mode — works with LM Studio's own chat
- ✅ Clipboard mode — works with any app
- ✅ Streaming support — responses appear as they're generated
- ✅ Source URLs in results — model can cite references
- ✅ Always-on-top floating window
- ✅ Zero interference when OFF
- ✅ Cross-platform (Windows, Mac, Linux)
- ✅ Open source, MIT License

---

## License

MIT License — free for everyone to use, modify, and share.
