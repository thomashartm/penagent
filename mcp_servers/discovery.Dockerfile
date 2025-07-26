FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install fastapi uvicorn requests

# Copy MCP server code
COPY src/owasp/owasp_server.py /app/owasp_server.py
WORKDIR /app

CMD ["uvicorn", "owasp_server:app", "--host", "0.0.0.0", "--port", "8003"] 