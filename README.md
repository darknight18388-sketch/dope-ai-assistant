# Dope-AI

Personal AI assistant: Gmail + Calendar + Gemini. Original code.

## Setup
```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # add GEMINI_API_KEY
```
Put Google `credentials.json` in this folder, then:
```bash
python main.py brief
python main.py drafts
```
Drafts are only saved to Gmail Drafts. Nothing is ever sent automatically.
