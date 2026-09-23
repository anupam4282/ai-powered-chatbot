# AI-Powered Chatbot

A complete customer-support/FAQ chatbot built with Python, NLTK, Transformers, Flask, and SQLite.

## Features

- Responsive chatbot web interface
- NLP preprocessing with NLTK
- FAQ/intent matching for reliable support answers
- Transformer-based contextual response fallback
- SQLite conversation logging
- Conversation history
- Clear chat button
- REST API
- Ready for local development and deployment

## 1. Requirements

- Python 3.10+
- pip
- Internet connection for the first Transformer model download

## 2. Create a virtual environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### macOS/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Run

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

The first time an open-ended message uses the Transformer model, Hugging Face Transformers downloads `distilgpt2`. The first download can take some time.

## 5. API

### Send a message

`POST /api/chat`

JSON:

```json
{
  "message": "How can I reset my password?"
}
```

Response:

```json
{
  "response": "If you forgot your password..."
}
```

### Get history

`GET /api/history`

### Clear history

`DELETE /api/history`

## Project Structure

```text
ai-powered-chatbot/
├── app.py
├── chatbot.py
├── database.py
├── requirements.txt
├── README.md
├── data/
│   └── chatbot.db          # created automatically
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── script.js
```

## How it works

1. User enters a message.
2. Flask receives it through `/api/chat`.
3. NLTK tokenizes, removes stop words, and lemmatizes the message.
4. The chatbot checks the FAQ intents.
5. If no FAQ matches, a Transformer model attempts a contextual response.
6. User and bot messages are saved in SQLite.
7. The response is returned to the browser.

## Important note

`distilgpt2` is a small general text-generation model, not a dedicated customer-support model. For a production chatbot, replace it with a support-tuned model or an LLM/API and add authentication, rate limiting, moderation, and stronger conversation-state management.

## Deployment

For a simple deployment, use a Python hosting service that supports Flask.

Typical commands:

Build/install:
```bash
pip install -r requirements.txt
```

Start:
```bash
gunicorn app:app
```

Add `gunicorn` to `requirements.txt` if your hosting provider requires it.
