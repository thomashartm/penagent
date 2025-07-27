FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies for FastMCP
RUN pip install fastmcp requests

# Copy MCP server code
COPY src/owasp/owasp_server.py /app/owasp_server.py
WORKDIR /app

CMD ["python", "owasp_server.py"] 