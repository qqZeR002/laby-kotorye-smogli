FROM python:3.12-slim

WORKDIR /app

# сначала зависимости: этот слой берётся из кэша, пока requirements.txt не менялся
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

# не запускаем приложение от root
RUN useradd --no-create-home appuser
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=5 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "main:app"]
