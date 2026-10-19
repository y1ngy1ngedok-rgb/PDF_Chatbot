# PDF Chatbot with Ollama

A command-line chatbot for general questions and questions about PDF content, powered by language models running locally through [Ollama](https://ollama.com/).

## Features

- Chat with an AI assistant about general topics.
- Extract text from a PDF and use it as context for answers.
- Choose between the `qwen2.5:1.5b` and `llama3.2:3b` models.
- Answers in the same language as the question and can include page numbers when available in the context.

## Requirements

- Python 3
- [Ollama](https://ollama.com/), running at `http://127.0.0.1:11434`
- The Python packages `requests` and `pypdf`

Install the required packages:

```bash
python -m pip install requests pypdf
```

Pull at least one model:

```bash
ollama pull qwen2.5:1.5b
```

Or:

```bash
ollama pull llama3.2:3b
```

## Usage

Run this command from the directory containing `crewai_pdf_chatbot.py`:

```bash
python crewai_pdf_chatbot.py
```

Choose one of the following modes when prompted:

1. **General chat** — Ask questions without using a document.
2. **Chat with a PDF** — Provide a PDF file when prompted.

You can optionally pass a PDF path as an argument:

```bash
python crewai_pdf_chatbot.py "Game Design Documentation-2.pdf"
```

If you select PDF mode, the program uses the provided file or prompts you for a filename if none was provided. You can use either a relative or an absolute path.

Next, select an installed model and enter your questions at the `คุณ:` prompt. Type `exit` or `quit` to end the conversation.

## Run with Docker Compose

Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) and start it. From the project directory, run:

```bash
docker compose up --build
```

Compose builds the chatbot image, starts Ollama, downloads `qwen2.5:1.5b` the first time, and then opens the interactive chatbot. The model is kept in a Docker volume for later runs. Stop the services with `Ctrl+C`, then run `docker compose down` to remove the containers.

To use a different model for the automatic download, set `OLLAMA_MODEL` before starting Compose:

```bash
OLLAMA_MODEL=llama3.2:3b docker compose up --build
```

To ask questions about a PDF, put the file in the `pdfs` directory and pass its path inside the container:

```bash
docker compose run --rm chatbot pdfs/my-document.pdf
```

## PDF Handling

The program extracts text from each page using `pypdf` and includes page labels in the context, such as `[Page 1]`. When answering questions about a document, it prioritizes the PDF content.

Limitations:

- Up to 12,000 characters of PDF text are included for each question.
- Scanned PDFs may not contain extractable text. The program displays a warning, but you can still use general chat mode.
- OCR is not included.

## Troubleshooting

- **Cannot connect to Ollama:** Make sure Ollama is running and reachable at `http://127.0.0.1:11434`.
- **Model is not installed:** Run `ollama pull <model-name>` using the model name shown by the program.
- **Cannot read the PDF:** Check the file path, read permissions, and that the file is a valid PDF.
