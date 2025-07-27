FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies for FastMCP
COPY src/rag/requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

# Copy MCP server code
COPY src/rag/rag_server.py /app/rag_server.py
WORKDIR /app

CMD ["sleep", "infinity"] 