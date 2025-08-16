FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    make \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 IN_DOCKER=1

# If you need Playwright in the container:
# RUN python -m playwright install --with-deps chromium

# Optionally run migrations at start (if desired):
# CMD make upgrade && make serve
CMD ["make", "serve"]
