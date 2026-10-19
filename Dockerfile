FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && useradd --create-home --uid 10001 app

COPY --chown=app:app crewai_pdf_chatbot.py .

USER app

ENTRYPOINT ["python", "crewai_pdf_chatbot.py"]
