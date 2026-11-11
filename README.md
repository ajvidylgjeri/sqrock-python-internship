# Sqrock IT Solutions — Python Internship (Phase 1)

Three **Flask** web applications demonstrating Python back-end development, templating, databases and image processing. The phase requires any 3 projects.

| # | Project | Folder | Stack | Highlights |
|---|---------|--------|-------|-----------|
| 1 | AI Chatbot Web App | [`ai-chatbot`](./ai-chatbot) | Flask | Chat UI, typing animation, dark mode, rule-based offline replies + optional live LLM |
| 2 | Hospital Management System | [`hospital-management-system`](./hospital-management-system) | Flask + SQLite | Patients, doctors, appointments, billing, dashboard, search |
| 3 | AI Image Generator | [`ai-image-generator`](./ai-image-generator) | Flask + Pillow | Prompt → generated image, download, offline generative art + optional live API |

## 🔑 Offline by default
The two "AI" apps run **with no API key** — the chatbot uses a rule-based engine and the image generator uses Pillow to create deterministic abstract art from your prompt. Each has a clearly marked integration point to switch to a real AI API via an environment variable (`OPENAI_API_KEY` / `IMAGE_API_KEY`), so they work for anyone out of the box and go live whenever you want.

## 🚀 Run any project
```bash
cd ai-chatbot                 # or another project folder
pip install -r requirements.txt
python app.py
# open http://127.0.0.1:5000
```

## 📚 Concepts demonstrated
Python · Flask (routing, templates, JSON APIs) · Jinja2 · SQLite (`sqlite3`) · Pillow image generation · front-end (HTML/CSS/JS) · graceful fallbacks & input validation

## 👤 Author
**Ajvi Dylgjeri** — Software Engineering student, University of New York Tirana.

---
*Built for the Sqrock IT Solutions internship program.*
