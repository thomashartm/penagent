FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install fastapi uvicorn

# Copy MCP server code
COPY src/rag/rag_server.py /app/rag_server.py
WORKDIR /app

CMD ["uvicorn", "rag_server:app", "--host", "0.0.0.0", "--port", "8004"] 