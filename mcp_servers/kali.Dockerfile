FROM kalilinux/kali-rolling

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    metasploit-framework \
    gobuster \
    hydra \
    nmap \
    curl \
    dnsutils \
    netcat-openbsd \
    python3 \
    python3-pip \
    python3-venv \
    git \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install FastMCP and dependencies with --break-system-packages flag
COPY src/kali/requirements.txt /app/requirements.txt
RUN pip3 install --break-system-packages -r /app/requirements.txt

# Copy MCP server code from src/kali directory
COPY src/kali/kali_server.py /app/kali_server.py
WORKDIR /app

# Use FastMCP server
CMD ["sleep", "infinity"] 