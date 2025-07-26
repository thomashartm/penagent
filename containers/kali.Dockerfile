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
    git \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

CMD ["tail", "-f", "/dev/null"] 