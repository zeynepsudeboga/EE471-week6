# 1) Base image: small Debian (bookworm) with Python 3.12 already installed
FROM python:3.12-slim-bookworm

# 2) System libraries the Azure Speech SDK needs on Linux (TLS + audio library)
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates libssl3 libasound2 \
    && rm -rf /var/lib/apt/lists/*

# 3) Print Python logs immediately instead of buffering them
ENV PYTHONUNBUFFERED=1

# 4) All following commands run inside /app in the container
WORKDIR /app

# 5) Install Python packages first, so this layer is cached when only the code changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6) Copy the application code (.dockerignore keeps .env and caches out)
COPY . .

# 7) Document the port the app listens on
EXPOSE 5001

# 8) Start Flask on 0.0.0.0 so it is reachable from outside the container
CMD ["flask", "--app", "app", "run", "--host=0.0.0.0", "--port=5001"]
