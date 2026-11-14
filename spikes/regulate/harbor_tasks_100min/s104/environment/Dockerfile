FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends curl bash ripgrep ca-certificates nodejs npm \
 && npm install -g @openai/codex && codex --version && pip install --no-cache-dir scipy==1.18.1 numpy==2.5.3 \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY app/ /app/
