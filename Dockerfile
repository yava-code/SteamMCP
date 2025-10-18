FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# The server reads STEAM_API_KEY from environment at runtime
# Expose default development port (if used by FastMCP/runner)
EXPOSE 8000

CMD ["python", "server.py"]