FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install fastapi uvicorn requests beautifulsoup4

# Copy MCP server code
COPY src/websearch/websearch_server.py /app/websearch_server.py
WORKDIR /app

CMD ["uvicorn", "websearch_server:app", "--host", "0.0.0.0", "--port", "8002"] 