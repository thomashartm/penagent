FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies for FastMCP
RUN pip install fastmcp

# Copy MCP server code
COPY src/rag/rag_server.py /app/rag_server.py
WORKDIR /app

CMD ["python", "rag_server.py"] 