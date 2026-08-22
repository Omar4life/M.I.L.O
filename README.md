# M.I.L.O

**M.I.L.O is a local AI assistant that helps you find and understand files on your own computer using natural language.**

> **M.I.L.O = My Intelligent Local Organizer**

<img width="1919" height="910" alt="Screenshot 2026-08-22 175208" src="https://github.com/user-attachments/assets/d702bc91-394c-421d-ae35-19263506c335" />

## Try M.I.L.O

**Live demo:** https://milo-stardance.vercel.app

The live demo is the M.I.L.O interface. To actually search and understand files on your computer, download and run the local M.I.L.O backend using github releases below:

**Releases:** https://github.com/Omar4life/M.I.L.O/releases

---

## What problem does M.I.L.O solve?

Finding something on your computer can be annoying when you don't remember the exact filename.

Instead of searching through folders manually, you can tell M.I.L.O what you mean:

> "Find my Spider-Man movie ticket."

or:

> "Find my school enrollment document."

M.I.L.O searches the folder you give it and uses a local AI model to understand what you're asking for.

It can also read the contents of documents, including scanned PDFs using OCR.

---

## Features

* **Natural-language file search** - search for files and folders without knowing their exact names.
* **Local AI** - uses Ollama and Qwen3:8B on your own computer.
* **PDF understanding** - searches text-based PDFs and reads their contents.
* **OCR for scanned PDFs** - detects when a PDF has no usable text and uses Tesseract OCR.
* **Conversation memory** - remembers the current conversation so follow-up questions like "what file did you find?" work.
* **Chat history** - create new chats and return to previous conversations.
* **Fast document search** - prioritizes likely files, skips common junk folders, and caches OCR results.
* **Local-first privacy** - files are processed on the user's computer instead of being uploaded to a remote AI service.

---

## Quick Start

### Windows

1. Download the latest release from the [Releases page](https://github.com/Omar4life/M.I.L.O/releases).
2. Extract the ZIP.
3. Open the extracted M.I.L.O folder.
4. Double-click:

```text
Start MILO.bat
```

The launcher checks for the required software, installs missing Python dependencies, checks Ollama, downloads the Qwen3:8B model if necessary, and starts the local backend.

On the first launch, downloading the AI model can take a while because the model is several GB.

After M.I.L.O starts:

1. Enter the folder you want M.I.L.O to search.
2. Ask a question in normal language.
3. M.I.L.O searches the selected folder and returns the most relevant results.

Example:

```text
Folder:
C:\Users\YourName\Downloads

Ask:
Find my Spider-Man movie ticket
```

---

## 🛠️ Requirements

M.I.L.O v1.0 is designed for **Windows**.

The automatic launcher handles most setup, but the PC needs:

* Windows 10 or Windows 11
* Internet access for the initial setup and model download
* Python 3.11 or newer
* Ollama
* Qwen3:8B
* Tesseract OCR
* The Python dependencies in `Backend/requirements.txt`

The launcher attempts to install missing dependencies automatically.

---

## 💻 Run M.I.L.O locally

For development, open a PowerShell terminal in:

```text
C:\M.I.L.O\M.I.L.O
```

Then:

```powershell
cd Backend
python -m uvicorn main:app --reload
```

The backend runs locally at:

```text
http://127.0.0.1:8000
```

You can then open the frontend from the `Frontend` folder.

---

## 🧠 How it works

M.I.L.O is designed around a local-first architecture.

```text
User
  ↓
M.I.L.O frontend
  ↓
Local FastAPI backend
  ↓
Search / document processing
  ↓
Ollama + Qwen3:8B
```

For documents, M.I.L.O uses a two-stage approach.

First, it tries to read normal document text quickly. If a PDF contains little or no usable text, M.I.L.O treats it as a possible scanned document and uses Tesseract OCR.

Search performance is important because a folder can contain hundreds or thousands of files. Instead of OCR-ing every PDF immediately, M.I.L.O prioritizes likely files, ignores common development folders such as `node_modules` and `.git`, and caches OCR results so the same document does not need to be processed repeatedly.

Conversation memory is kept separately for each chat, allowing follow-up questions such as:

```text
Find my Spider-Man ticket

What file did you find?

What did I just ask you to find?
```

The goal is for M.I.L.O to understand the conversation instead of requiring the user to repeat filenames and context.

---

## 🔒 Privacy

M.I.L.O is built around local processing.

The files you choose to search stay on your computer, and the AI model runs locally through Ollama.

M.I.L.O only searches the folder that you explicitly provide.

For example, you can choose:

```text
C:\Users\YourName\Documents
```

or:

```text
C:\Users\YourName\OneDrive
```

depending on what you want M.I.L.O to access.

---

## 📁 Project Structure

```text
M.I.L.O/
├── Backend/
│   ├── ai.py
│   ├── file_manager.py
│   ├── main.py
│   └── requirements.txt
│
├── Frontend/
│   ├── app.js
│   ├── index.html
│   └── style.css
│
├── Start MILO.bat
├── .gitignore
└── README.md
```

---

## 🔧 Technical Stack

**Frontend**

* HTML
* CSS
* JavaScript

**Backend**

* Python
* FastAPI
* Uvicorn

**AI**

* Ollama
* Qwen3:8B

**Document processing**

* pypdf
* PyMuPDF
* Tesseract OCR
* Pillow

---

## 🧪 Example Use Cases

### Find a file

```text
Find my Spider-Man ticket
```

### Find a document by meaning

```text
Find my school enrollment document
```

### Ask about a document

```text
What school is this document from?
```

### Continue the conversation

```text
Find my Spider-Man ticket

What file did you find?
```

M.I.L.O uses the conversation context to understand follow-up questions.

---

## 🛣️ Roadmap

### v1.0

* Natural-language search
* Local AI
* PDF reading
* OCR for scanned PDFs
* Conversation memory
* Chat history
* Faster search and OCR caching

### v1.1

The next major step is **file actions**.

Planned actions include:

* Rename files
* Move files
* Create folders
* Organize files
* Safe confirmation before changing anything

The goal is to move M.I.L.O from **"find my files"** to **"help organize my computer."**

---

## 🙏 Credits

M.I.L.O uses several open-source projects and tools:

* [Ollama](https://ollama.com/)
* [Qwen](https://github.com/QwenLM/Qwen)
* [FastAPI](https://fastapi.tiangolo.com/)
* [Uvicorn](https://www.uvicorn.org/)
* [pypdf](https://github.com/py-pdf/pypdf)
* [PyMuPDF](https://pymupdf.readthedocs.io/)
* [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
* [Pillow](https://python-pillow.org/)

---

## ⭐ Why I built M.I.L.O

M.I.L.O started from a simple idea:

**What if you could just tell your computer what you're looking for instead of remembering where you put it?**

M.I.L.O is my attempt at making that idea work locally, with the user's own files and a local AI model.
