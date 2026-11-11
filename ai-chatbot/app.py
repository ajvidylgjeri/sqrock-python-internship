"""
AI Chatbot Web Application — Sqrock IT Solutions Python Internship (Phase 1, Task 1)

A Flask chatbot web app with a clean chat interface. Works out of the box in
OFFLINE mode (a rule-based reply engine) so it runs for anyone with no API key.
To use a real LLM instead, set the OPENAI_API_KEY environment variable and
install `openai` — the app will automatically switch to live mode.

Run:
    pip install -r requirements.txt
    python app.py
    # open http://127.0.0.1:5000

Author: Ajvi Dylgjeri
"""
import os
import re
import random
import datetime
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "").strip()


# ---------------------------------------------------------------------------
# Offline rule-based reply engine (default — no API key needed)
# ---------------------------------------------------------------------------
RULES = [
    (r"\b(hi|hello|hey|greetings)\b",
     ["Hello! 👋 I'm Sqrock Assistant. How can I help you today?",
      "Hi there! Ask me anything — I'm happy to help."]),
    (r"\b(how are you|how's it going)\b",
     ["I'm just code, but I'm running great! How about you?"]),
    (r"\b(your name|who are you)\b",
     ["I'm Sqrock Assistant, a demo chatbot built with Python and Flask."]),
    (r"\b(time|what time)\b",
     [lambda: "It's " + datetime.datetime.now().strftime("%H:%M") + " right now."]),
    (r"\b(date|today)\b",
     [lambda: "Today is " + datetime.datetime.now().strftime("%A, %d %B %Y") + "."]),
    (r"\b(help|what can you do)\b",
     ["I can chat, answer simple questions, tell the time and date, and explain "
      "what I am. Try asking me about Python, or say hello!"]),
    (r"\b(python)\b",
     ["Python is a versatile, readable programming language — great for web apps, "
      "data science and automation. This chatbot's backend is written in it!"]),
    (r"\b(flask)\b",
     ["Flask is a lightweight Python web framework. It powers this app's backend "
      "and routes your messages to the reply engine."]),
    (r"\b(thank|thanks)\b",
     ["You're welcome! 😊", "Anytime! Happy to help."]),
    (r"\b(bye|goodbye|see you)\b",
     ["Goodbye! Come back any time. 👋"]),
    (r"\b(joke)\b",
     ["Why do programmers prefer dark mode? Because light attracts bugs! 🐛"]),
]

FALLBACKS = [
    "Interesting! Tell me more about that.",
    "I'm a demo bot, so my knowledge is limited — but I'm listening. Could you rephrase?",
    "Hmm, I'm not sure about that one yet. Try asking about Python, the time, or say hello!",
]


def offline_reply(message: str) -> str:
    msg = message.lower().strip()
    for pattern, responses in RULES:
        if re.search(pattern, msg):
            choice = random.choice(responses)
            return choice() if callable(choice) else choice
    return random.choice(FALLBACKS)


# ---------------------------------------------------------------------------
# Optional live mode (used automatically if OPENAI_API_KEY is set)
# ---------------------------------------------------------------------------
def live_reply(message: str) -> str:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are Sqrock Assistant, a helpful, concise assistant."},
                {"role": "user", "content": message},
            ],
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:  # fall back gracefully if the API call fails
        return f"(Live mode error, using offline reply) {offline_reply(message)}"


def get_reply(message: str) -> str:
    if OPENAI_API_KEY:
        return live_reply(message)
    return offline_reply(message)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    mode = "live" if OPENAI_API_KEY else "offline"
    return render_template("index.html", mode=mode)


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"reply": "Please type a message."}), 400
    return jsonify({"reply": get_reply(message)})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
