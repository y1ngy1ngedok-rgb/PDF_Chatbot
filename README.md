# PDF Chatbot with Ollama

A command-line chatbot for general questions and questions about PDF documents. It sends prompts to a locally running [Ollama](https://ollama.com/) server, so you can run supported language models on your own machine.

## Features

- Chat about general topics or ask questions about a PDF.
- Select either `qwen2.5:1.5b` or `llama3.2:3b`.
- Answer in the language of the question, with page references when available in the PDF context.
- Run locally with Python or in Docker Compose.

## Requirements

- Python and the packages listed in [`requirements.txt`](requirements.txt) for local use. The Docker image uses Python 3.12.
- [Ollama](https://ollama.com/) running and reachable at `http://127.0.0.1:11434` for local use.

Install the Python dependencies:

```bash
python -m pip install -r requirements.txt
```

Install at least one supported model in Ollama:

```bash
ollama pull qwen2.5:1.5b
```

Or:

```bash
ollama pull llama3.2:3b
```

## Run locally

Start Ollama, then run the chatbot from the project directory:

```bash
python PDF_Chatbot.py
```

[`run_chatbot.py`](run_chatbot.py) is also available as a compatibility launcher:

```bash
python run_chatbot.py
```

Choose a mode when prompted:

1. **General chat** — ask questions without a document.
2. **Chat with a PDF** — enter a PDF path when prompted, or pass it as an argument:

   ```bash
   python PDF_Chatbot.py "path/to/document.pdf"
   ```

Relative PDF paths are resolved from the project directory; absolute paths are also accepted. After choosing a mode, select one of the two supported models. The program reports if the selected model is not installed and shows the `ollama pull` command needed to install it. Type `exit` or `quit` at the `คุณ:` prompt to end the conversation.

If Ollama is running at a different address, set `OLLAMA_URL` before starting the program:

```bash
OLLAMA_URL=http://localhost:11434 python PDF_Chatbot.py
```

## Run with Docker Compose

Install and start [Docker Desktop](https://www.docker.com/products/docker-desktop/), then run from the project directory:

```bash
docker compose up --build
```

Compose builds the chatbot image, starts Ollama, pulls `qwen2.5:1.5b` by default, and starts the interactive chatbot. Ollama models are stored in a Docker volume and are retained between runs. Stop the services with `Ctrl+C`; remove the containers with:

```bash
docker compose down
```

To pull a different model during startup, set `OLLAMA_MODEL`:

```bash
OLLAMA_MODEL=llama3.2:3b docker compose up --build
```

To chat with a PDF in Compose, place the file in the project’s `pdfs` directory and pass its path inside the container:

```bash
docker compose run --rm chatbot pdfs/my-document.pdf
```

The `pdfs` directory is mounted read-only in the chatbot container.

## PDF handling and limitations

The chatbot extracts text from each page with `pypdf` and labels it with its page number, for example `[Page 1]`. Up to 12,000 characters of extracted text are included in each prompt. PDF text is prioritized for document questions; if the relevant information is not present in the supplied text, the assistant is instructed to say so.

Scanned PDFs without extractable text are not processed with OCR. The chatbot warns when no text is found; OCR is not included.

## Troubleshooting

- **Cannot connect to Ollama:** Start Ollama and check that it is reachable at `http://127.0.0.1:11434`, or set `OLLAMA_URL` to its address.
- **Model is not installed:** Run `ollama pull <model-name>` for the model you selected. In Compose, set `OLLAMA_MODEL` to choose which model is pulled automatically.
- **Cannot read the PDF:** Check that the path is correct, the file is readable, and it is a valid PDF. For Compose, ensure the file is under `pdfs/` and use its container path, such as `pdfs/my-document.pdf`.
