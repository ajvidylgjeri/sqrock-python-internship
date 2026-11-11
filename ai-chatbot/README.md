# AI Chatbot Web Application (Flask)

Sqrock IT Solutions Python Internship — Phase 1, Task 1.

A chatbot web app with a clean chat interface. Runs **offline out of the box** using a rule-based reply engine; switches to a real LLM automatically if an API key is provided.

## Features
- Attractive chat UI with message bubbles and avatars
- Animated "typing…" indicator
- User message & bot response flow (Flask JSON API)
- **Dark mode** toggle (persisted in `localStorage`)
- Responsive design
- Offline rule-based replies (greetings, time/date, jokes, Python/Flask facts, fallbacks)
- Optional live mode: set `OPENAI_API_KEY` and install `openai` to use `gpt-4o-mini`

## Run
```bash
pip install -r requirements.txt
python app.py        # http://127.0.0.1:5000
```

### Live AI (optional)
```bash
pip install openai
export OPENAI_API_KEY=sk-...      # Windows: set OPENAI_API_KEY=...
python app.py                      # header will show "Live AI"
```

## Tech
Python · Flask · HTML/CSS/JS · fetch API.

**Author:** Ajvi Dylgjeri
