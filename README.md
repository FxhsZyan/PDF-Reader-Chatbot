# PDF ChatBot — Powered by Groq

A fast, lightweight desktop chatbot that lets you upload any PDF and ask questions about it — powered by Groq's free LLaMA API. Built with Python and Tkinter, no internet browser required.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-LLaMA%203.3%2070B-orange)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Preview

> Dark-themed desktop UI with a violet accent, real-time chat, and PDF status indicator.

---

## Features

-  **Full PDF reading** — indexes every page, no page limits
-  **Smart retrieval** — finds the most relevant sections per question using keyword + phrase scoring
-  **Roman numeral aware** — asking "article 7" correctly finds "ARTICLE VII" and vice versa
-  **Groq-powered** — uses LLaMA 3.3 70B for fast, free AI responses
-  **Native desktop UI** — built with Tkinter, runs offline (no browser needed)
-  **Conversation memory** — remembers the last 6 turns for follow-up questions
-  **Auto-retry** — handles rate limits and server errors gracefully

---

## Project Structure

```
pdf-chatbot/
├── app.py          # Tkinter UI — window, buttons, chat display
├── chatbot.py      # PDF extraction, chunking, retrieval, Groq API calls
├── config.py       # API key and model name
└── README.md
```

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/pdf-chatbot.git
cd pdf-chatbot
```

### 2. Install dependencies

```bash
pip install groq PyPDF2
```

### 3. Add your Groq API key

Open `config.py` and paste your key:

```python
API_KEY = "your_groq_api_key_here"
MODEL   = "llama-3.3-70b-versatile"
```

Get a free API key at [console.groq.com](https://console.groq.com).

### 4. Run the app

```bash
python app.py
```

---

## How It Works

### PDF Indexing

When you upload a PDF, the app:
1. Extracts text from every page using `PyPDF2`
2. Tags each page with its page number (`[Page N]`)
3. Splits the full text into **overlapping 7,000-character chunks** (1,000-char overlap so context isn't lost at boundaries)

### Smart Retrieval

When you ask a question, the app:
1. Expands your query — e.g. `"article 7"` → also searches for `"VII"`, `"vii"`
2. Scores every chunk using:
   - **+20 pts** for an exact `"article [numeral]"` phrase match
   - **+8 pts** for a `"section [numeral]"` phrase match
   - **+3 pts** for a whole-word keyword match
   - **+1 pt** for a substring match
3. Sends the **top 5 highest-scoring chunks** to Groq as context
4. Returns the AI's answer, grounded only in those sections

This approach means the full document is always indexed, but only the relevant parts are sent to the AI — keeping responses fast and accurate.

---

## Configuration

All tuning knobs are at the top of `chatbot.py`:

| Variable | Default | Description |
|---|---|---|
| `CHUNK_SIZE` | `7000` | Characters per chunk |
| `OVERLAP` | `1000` | Overlap between chunks |
| `TOP_CHUNKS` | `5` | Chunks sent to Groq per query |

---

## Dependencies

| Package | Purpose |
|---|---|
| `groq` | Groq API client |
| `PyPDF2` | PDF text extraction |
| `tkinter` | Desktop UI (bundled with Python) |

---

## Limitations

- Works best with **text-based PDFs** — scanned/image PDFs have no extractable text
- Groq's free tier has **rate limits** — the app retries automatically, but very long sessions may hit limits
- Answers are limited to what appears in the **retrieved chunks** — if a topic scores low, try rephrasing with the exact article or section number

---

## License

MIT — free to use, modify, and distribute.
