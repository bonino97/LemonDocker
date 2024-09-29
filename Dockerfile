# LemonBooster Dockerfile
# Base image
FROM ubuntu:22.04

# Set environment variables to avoid prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Update and install basic dependencies
RUN apt-get update && \
    apt-get install -y \
        build-essential \
        git \
        wget \
        curl \
        python3 \
        python3-pip \
        python3-dev \
        python3-setuptools \
        python3-wheel \
        python3-venv \
        gnupg2 \
        software-properties-common \
        ca-certificates \
        libssl-dev \
        libffi-dev \
        locales \
        unzip \
        jq \
        libpcap-dev \
        libldns-dev \
        libnet-ssleay-perl \
        openssl \
        libwhisker2-perl \
        ruby \
        ruby-dev \
        libxml2-dev \
        libxslt1-dev \
        zlib1g-dev \
        libmysqlclient-dev \
        libsqlite3-dev \
        libpq-dev \
        libpcap0.8-dev \
        libgmp-dev \
        libyaml-dev \
        gcc \
        make \
        cmake \
        perl \
        default-jdk && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Go (latest version)
RUN wget https://golang.org/dl/go1.21.1.linux-amd64.tar.gz && \
    tar -C /usr/local -xzf go1.21.1.linux-amd64.tar.gz && \
    rm go1.21.1.linux-amd64.tar.gz

# Set Go environment variables
ENV GOROOT=/usr/local/go
ENV GOPATH=/go
ENV PATH=$PATH:/usr/local/go/bin:$GOPATH/bin

# Create Go workspace directory
RUN mkdir -p $GOPATH/src $GOPATH/bin

# Install Rust (for Rust-based tools)
RUN curl https://sh.rustup.rs -sSf | bash -s -- -y
ENV PATH="$PATH:/root/.cargo/bin"

# Install Node.js (latest version)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs

# Upgrade pip
RUN pip3 install --upgrade pip

# Install Java (for tools that require Java)
RUN apt-get update && apt-get install -y default-jdk

# -----------------------------
# Install Go-based tools
# -----------------------------

# Subdomain Enumeration

## Amass
RUN go install -v github.com/owasp-amass/amass/v3/...@latest

## Subfinder
RUN go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest

## ASNmap
RUN go install -v github.com/projectdiscovery/asnmap/cmd/asnmap@latest

## Assetfinder
RUN go install -v github.com/tomnomnom/assetfinder@latest

## GoBuster
RUN go install -v github.com/OJ/gobuster/v3@latest

## Chaos
RUN go install -v github.com/projectdiscovery/chaos-client/cmd/chaos@latest

# Active Subdomain Verification

## Httpx
RUN go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest

## Httprobe
RUN go install -v github.com/tomnomnom/httprobe@latest

## Dnsx
RUN go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest

# Spidering and Crawling

## Gospider
RUN go install -v github.com/jaeles-project/gospider@latest

## Hakrawler
RUN go install -v github.com/hakluke/hakrawler@latest

## Katana
RUN go install -v github.com/projectdiscovery/katana/cmd/katana@latest

# Port and Service Scanning

## Naabu
RUN go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest

## Tlsx
RUN go install -v github.com/projectdiscovery/tlsx/cmd/tlsx@latest

# Technology Fingerprinting

# Webanalyze
RUN go install -v github.com/rverton/webanalyze/cmd/webanalyze@latest

# Automated Vulnerability Scanning

## Nuclei
RUN go install -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest && \
    nuclei -update-templates

## Interactsh client
RUN go install -v github.com/projectdiscovery/interactsh/cmd/interactsh-client@latest

# Screenshots

## GoWitness
RUN go install -v github.com/sensepost/gowitness@latest

## GitHub Subdomains
RUN go install -v github.com/gwen001/github-subdomains@latest

# Dirsearch (Python-based but added here for categorization)
RUN git clone https://github.com/maurosoria/dirsearch.git /opt/dirsearch

# -----------------------------
# Install C-based tools
# -----------------------------

# Active Subdomain Verification

## MassDNS
RUN git clone https://github.com/blechschmidt/massdns.git /opt/massdns && \
    cd /opt/massdns && \
    make && \
    cp bin/massdns /usr/local/bin/

# Port and Service Scanning

## Masscan
RUN git clone https://github.com/robertdavidgraham/masscan /opt/masscan && \
    cd /opt/masscan && \
    make && \
    cp bin/masscan /usr/local/bin/

# -----------------------------
# Install Python-based tools
# -----------------------------

# Subdomain Enumeration

## Sublist3r
RUN git clone https://github.com/aboul3la/Sublist3r.git /opt/Sublist3r && \
    pip3 install -r /opt/Sublist3r/requirements.txt && \
    ln -s /opt/Sublist3r/sublist3r.py /usr/local/bin/sublist3r

## KnockPy
RUN git clone https://github.com/guelfoweb/knock.git /opt/knock && \
    cd /opt/knock && \
    python3 setup.py install

## Altdns
RUN git clone https://github.com/infosec-au/altdns.git /opt/altdns && \
    cd /opt/altdns && \
    pip3 install -r requirements.txt && \
    python3 setup.py install

# Subdomain Scanners
## Subrake
RUN git clone https://github.com/hash3liZer/Subrake.git /opt/subrake && \
    cd /opt/subrake && \
    pip3 install -r requirements.txt

# JavaScript Files

## LinkFinder
RUN git clone https://github.com/GerbenJavado/LinkFinder.git /opt/LinkFinder && \
    pip3 install -r /opt/LinkFinder/requirements.txt && \
    ln -s /opt/LinkFinder/linkfinder.py /usr/local/bin/linkfinder

# Scanners

## SQLMap
RUN git clone --depth 1 https://github.com/sqlmapproject/sqlmap.git /opt/sqlmap && \
    ln -s /opt/sqlmap/sqlmap.py /usr/local/bin/sqlmap

# Automated Vulnerability Scanning

## SSLyze
RUN pip3 install sslyze

# Screenshots

## EyeWitness
RUN git clone https://github.com/FortyNorthSecurity/EyeWitness.git /opt/EyeWitness && \
    cd /opt/EyeWitness/Python/setup && \
    bash setup.sh

# JSON Manipulation

## JQ (already installed)

# OSINT
# TheHarvester
RUN git clone https://github.com/laramies/theHarvester.git /opt/theHarvester && \
    cd /opt/theHarvester && \
    pip3 install -r requirements/base.txt && \
    ln -s /opt/theHarvester/theHarvester.py /usr/local/bin/theHarvester

# -----------------------------
# Install Perl-based tools
# -----------------------------

# Automated Vulnerability Scanning

## Nikto
RUN git clone https://github.com/sullo/nikto.git /opt/nikto && \
    ln -s /opt/nikto/program/nikto.pl /usr/local/bin/nikto

# -----------------------------
# Install Ruby-based tools
# -----------------------------

# Technology Fingerprinting

## WhatWeb
RUN git clone https://github.com/urbanadventurer/WhatWeb /opt/WhatWeb && \
    cd /opt/WhatWeb && \
    gem install bundler && \
    bundle install && \
    ln -s /opt/WhatWeb/whatweb /usr/local/bin/whatweb

# CMS Scanners

## WPScan
RUN gem install wpscan

# -----------------------------
# Install other tools
# -----------------------------

# Subdomain Enumeration

## Findomain
RUN wget https://github.com/Findomain/Findomain/releases/latest/download/findomain-linux.zip && \
    unzip findomain-linux.zip && \
    chmod +x findomain && \
    mv findomain /usr/local/bin/ && \
    rm findomain-linux.zip

# Port and Service Scanning

## Nmap
RUN apt-get update && \
    apt-get install -y nmap

# Git Tools

## shhgit
RUN git clone https://github.com/eth0izzle/shhgit.git /opt/shhgit && \
    cd /opt/shhgit && \
    go build && \
    mv shhgit /usr/local/bin/

# Wordlists

## SecLists
RUN git clone https://github.com/danielmiessler/SecLists.git /opt/SecLists

## Commonspeak2-Wordlists
RUN git clone https://github.com/assetnote/commonspeak2-wordlists.git /opt/commonspeak2-wordlists

## BBH-Lists
RUN git clone https://github.com/bonino97/BBH-Lists.git /opt/BBH-Lists

## DirBuster Wordlists
RUN git clone https://github.com/daviddias/node-dirbuster.git /opt/node-dirbuster

# Install CloudEnum (for Cloud Discovery)
RUN git clone https://github.com/initstring/cloud_enum.git /opt/cloud_enum && \
    pip3 install -r /opt/cloud_enum/requirements.txt

# Install S3Scanner (for AWS Bucket Enumeration)
RUN go install -v github.com/sa7mon/s3scanner@latest

# Install GCPBucketBrute (for GCP Bucket Enumeration)
RUN git clone https://github.com/RhinoSecurityLabs/GCPBucketBrute.git /opt/GCPBucketBrute

# Install Wfuzz
RUN pip3 install wfuzz

# Install Flask (for the API)
RUN pip3 install flask

# Clean up
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /root/

# Expose the API port
EXPOSE 8000

# Copy and set permissions for the entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Copy API files
COPY api /opt/api

# Default command
CMD ["/entrypoint.sh"]
