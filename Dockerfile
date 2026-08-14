FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATABASE_URL=sqlite:////data/lucky_lab.db

WORKDIR /app
COPY pyproject.toml ./
COPY app ./app
COPY migrations ./migrations
COPY docker-entrypoint.sh ./docker-entrypoint.sh
RUN pip install --no-cache-dir . && chmod +x /app/docker-entrypoint.sh

EXPOSE 5020
ENTRYPOINT ["/app/docker-entrypoint.sh"]
