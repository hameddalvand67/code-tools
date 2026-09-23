FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends libpq5 curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//' /entrypoint.sh && chmod +x /entrypoint.sh \
    && mkdir -p /app/staticfiles

EXPOSE 8000
HEALTHCHECK --interval=20s --timeout=5s --start-period=40s --retries=8 \
    CMD curl -fsS http://127.0.0.1:8000/health/ >/dev/null || exit 1
ENTRYPOINT ["/entrypoint.sh"]
