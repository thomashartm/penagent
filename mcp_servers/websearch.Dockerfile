FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies for FastMCP
COPY src/websearch/requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

# Copy MCP server code
COPY src/websearch/websearch_server.py /app/websearch_server.py
WORKDIR /app

CMD ["python3", "websearch_server.py"] 