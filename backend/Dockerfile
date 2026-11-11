FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MYCODEX_DB_PATH=/data/jobs.sqlite3 \
    PORT=8000

WORKDIR /app
COPY requirements.txt pyproject.toml ./
RUN python -m pip install --no-cache-dir -r requirements.txt && mkdir -p /data
COPY app ./app
RUN python -m pip install --no-cache-dir --no-deps .

VOLUME ["/data"]
EXPOSE 8000
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
