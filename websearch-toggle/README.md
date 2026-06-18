# WebSearch Toggle

Gives your local AI model (Ollama / LM Studio) real-time web search capability.

---

## Install

```bash
git clone https://github.com/YOUR_USERNAME/websearch-toggle
cd websearch-toggle
pip install -r requirements.txt
python main.py
```

---

## How It Works

Two modes depending on which app you use:

### For LM Studio's built-in chat (Clipboard mode)

LM Studio's own chat talks to the model *directly* — it doesn't go through
the HTTP server port. So a proxy can't intercept it.

**You must use Clipboard mode:**
1. Type your question
2. Copy it (Ctrl+A then Ctrl+C)
3. Press **Ctrl+Shift+Enter** — web results are fetched and added
4. Paste back (Ctrl+A then Ctrl+V)
5. Press Enter to send

### For Open WebUI / external apps (Proxy mode)

External apps connect via HTTP, so our proxy can intercept requests.

1. Keep LM Studio server on port 1234
2. Toggle ON → proxy runs on port 8000
3. In Open WebUI Settings, set API URL to `http://localhost:8000`
4. Chat normally — web results added automatically

---

## Step-by-Step (Clipboard mode — recommended)

**Step 1:** Open LM Studio → load a model → **Developer tab** → **Start Server**

**Step 2:** Open Command Prompt:
```
cd C:\Users\neera\DOT-WEB-SCARPER\websearch-toggle
python main.py
```

**Step 3:** In the toggle window, **"LM Studio Chat (Clipboard)"** is selected

**Step 4:** Click the **red OFF** button → turns **green ON**

**Step 5:** In LM Studio, type your question, then:
- **Ctrl+A** → selects your question
- **Ctrl+C** → copies it
- **Ctrl+Shift+Enter** → injects web results into clipboard
- **Ctrl+A** → selects your question again
- **Ctrl+V** → pastes question + web results
- **Enter** → sends to the model

---

## Troubleshooting

| Problem | Fix |
|---------|------|
| No web results in answer | Make sure toggle is **ON** (green) |
| Ctrl+Shift+Enter not working | Run Command Prompt as **Administrator** |
| "Clipboard empty" message | Copy your question first (Ctrl+C) |
| Proxy mode not connecting | Point your app to `http://localhost:8000` |
| Model says "no internet" | Web results are in your prompt — model sees them as text |

---

## License

MIT License
