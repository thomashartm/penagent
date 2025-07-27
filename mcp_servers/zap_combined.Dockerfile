FROM ghcr.io/zaproxy/zaproxy:stable

# Install Python and dependencies for MCP server
USER root
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies for FastMCP server with --break-system-packages flag
RUN pip3 install --break-system-packages fastmcp requests

# Copy MCP server code (FastMCP version)
COPY src/zap/zap_server.py /app/zap_server.py
WORKDIR /app

# Create startup script that runs both ZAP daemon and MCP server
COPY <<EOF /app/startup.sh
#!/bin/bash
# Start ZAP daemon in background
zap.sh -daemon -host 0.0.0.0 -port 8090 -config api.disablekey=true -config api.addrs.addr.name=.* -config api.addrs.addr.regex=true &

# Wait for ZAP to be ready
echo "Waiting for ZAP daemon to start..."
while ! curl -s http://localhost:8090/JSON/core/view/version/ > /dev/null; do
    sleep 2
done
echo "ZAP daemon is ready!"

# Start MCP server
echo "Starting ZAP MCP server..."
python3 zap_server.py
EOF

RUN chmod +x /app/startup.sh

# Expose both ports
EXPOSE 8090 8005

# Use the startup script
CMD ["/app/startup.sh"] 