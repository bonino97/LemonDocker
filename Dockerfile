# LemonBooster Dockerfile
# Base image
FROM ubuntu:22.04

# Establecer variables de entorno para evitar prompts durante la instalación
ENV DEBIAN_FRONTEND=noninteractive

# Actualizar e instalar dependencias básicas
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
        gcc \
        make \
        cmake \
        perl \
        default-jdk && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Instalar Go (última versión)
RUN wget https://golang.org/dl/go1.21.1.linux-amd64.tar.gz &&
    tar -C /usr/local -xzf go1.21.1.linux-amd64.tar.gz &&
    rm go1.21.1.linux-amd64.tar.gz

# Configurar variables de entorno para Go
ENV GOROOT=/usr/local/go
ENV GOPATH=/go
ENV PATH=$PATH:/usr/local/go/bin:$GOPATH/bin

# Crear directorio de trabajo para Go
RUN mkdir -p $GOPATH/src $GOPATH/bin

# Instalar Rust (para herramientas basadas en Rust)
RUN curl https://sh.rustup.rs -sSf | bash -s -- -y
ENV PATH=$PATH:/root/.cargo/bin

# Instalar Node.js (última versión)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - &&
    apt-get install -y nodejs

# Actualizar pip
RUN pip3 install --upgrade pip

# Instalar Java (para herramientas que requieren Java)
RUN apt-get update && apt-get install -y default-jdk

# -----------------------------
# Instalar herramientas basadas en Go
# -----------------------------

# Enumeración de Subdominios

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

# Verificación de Subdominios Activos

## Httpx
RUN go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest

## Httprobe
RUN go install -v github.com/tomnomnom/httprobe@latest

## Dnsx
RUN go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest

# Spidering y Crawling

## Gospider
RUN go install -v github.com/jaeles-project/gospider@latest

## Hakrawler
RUN go install -v github.com/hakluke/hakrawler@latest

## Katana
RUN go install -v github.com/projectdiscovery/katana/cmd/katana@latest

# Escaneo de Puertos y Servicios

## Naabu
RUN go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest

## Tlsx
RUN go install -v github.com/projectdiscovery/tlsx/cmd/tlsx@latest

# Fingerprinting de Tecnologías

## Webanalyze
RUN go install -v github.com/rverton/webanalyze@latest

# Escaneo de Vulnerabilidades Automatizado

## Nuclei
RUN go install -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest &&
    nuclei -update-templates

## Interactsh client
RUN go install -v github.com/projectdiscovery/interactsh/cmd/interactsh-client@latest

# Screenshots

## Aquatone
RUN go install -v github.com/michenriksen/aquatone@latest

## GoWitness
RUN go install -v github.com/sensepost/gowitness@latest

# Dirsearch (Python-based but added here for categorization)
RUN git clone https://github.com/maurosoria/dirsearch.git /opt/dirsearch

# -----------------------------
# Instalar herramientas basadas en C
# -----------------------------

# Verificación de Subdominios Activos

## MassDNS
RUN git clone https://github.com/blechschmidt/massdns.git /opt/massdns &&
    cd /opt/massdns &&
    make &&
    cp bin/massdns /usr/local/bin/

# Escaneo de Puertos y Servicios

## Masscan
RUN git clone https://github.com/robertdavidgraham/masscan /opt/masscan &&
    cd /opt/masscan &&
    make &&
    cp bin/masscan /usr/local/bin/

# -----------------------------
# Instalar herramientas basadas en Python
# -----------------------------

# Enumeración de Subdominios

## Sublist3r
RUN git clone https://github.com/aboul3la/Sublist3r.git /opt/Sublist3r &&
    pip3 install -r /opt/Sublist3r/requirements.txt &&
    ln -s /opt/Sublist3r/sublist3r.py /usr/local/bin/sublist3r

## KnockPy
RUN git clone https://github.com/guelfoweb/knock.git /opt/knock &&
    cd /opt/knock &&
    python3 setup.py install

## Subjack
RUN git clone https://github.com/haccer/subjack.git /opt/subjack &&
    cd /opt/subjack &&
    go build &&
    mv subjack /usr/local/bin/

## Altdns
RUN git clone https://github.com/infosec-au/altdns.git /opt/altdns &&
    cd /opt/altdns &&
    pip3 install -r requirements.txt &&
    python3 setup.py install

## GitHub Subdomains
RUN git clone https://github.com/gwen001/github-subdomains.git /opt/github-subdomains &&
    cd /opt/github-subdomains &&
    pip3 install -r requirements.txt

# Subdomain Scanners

## Subrake
RUN git clone https://github.com/Hakin9/Subrake.git /opt/subrake &&
    cd /opt/subrake &&
    pip3 install -r requirements.txt

# Crawlers

## Crawler
RUN git clone https://github.com/ghostlulzhacks/crawler.git /opt/crawler

## Wayback Machine Script
RUN git clone https://github.com/ghostlulzhacks/waybackMachine.git /opt/waybackMachine

# JavaScript Files

## LinkFinder
RUN git clone https://github.com/GerbenJavado/LinkFinder.git /opt/LinkFinder &&
    pip3 install -r /opt/LinkFinder/requirements.txt &&
    ln -s /opt/LinkFinder/linkfinder.py /usr/local/bin/linkfinder

## JSSearch
RUN git clone https://github.com/incogbyte/jsearch.git /opt/jsearch &&
    cd /opt/jsearch &&
    pip3 install -r requirements.txt

# CMS Scanners

## CMSMap
RUN git clone https://github.com/Dionach/CMSmap.git /opt/CMSmap &&
    cd /opt/CMSmap &&
    pip3 install -r requirements.txt &&
    ln -s /opt/CMSmap/cmsmap.py /usr/local/bin/cmsmap

# Scanners

## Tplmap
RUN git clone https://github.com/epinna/tplmap.git /opt/tplmap &&
    cd /opt/tplmap &&
    pip3 install -r requirements.txt &&
    ln -s /opt/tplmap/tplmap.py /usr/local/bin/tplmap

## SQLMap
RUN git clone --depth 1 https://github.com/sqlmapproject/sqlmap.git /opt/sqlmap &&
    ln -s /opt/sqlmap/sqlmap.py /usr/local/bin/sqlmap

# Escaneo de Vulnerabilidades Automatizado

## SSLyze
RUN pip3 install sslyze

# Screenshots

## EyeWitness
RUN git clone https://github.com/FortyNorthSecurity/EyeWitness.git /opt/EyeWitness &&
    cd /opt/EyeWitness/Python/setup &&
    bash setup.sh

# JSON Manipulation

## JQ (ya instalado)

# -----------------------------
# Instalar herramientas basadas en Perl
# -----------------------------

# Escaneo de Vulnerabilidades Automatizado

## Nikto
RUN git clone https://github.com/sullo/nikto.git /opt/nikto &&
    ln -s /opt/nikto/program/nikto.pl /usr/local/bin/nikto

# -----------------------------
# Instalar herramientas basadas en Ruby
# -----------------------------

# Fingerprinting de Tecnologías

## WhatWeb
RUN git clone https://github.com/urbanadventurer/WhatWeb /opt/WhatWeb &&
    cd /opt/WhatWeb &&
    gem install bundler &&
    bundle install &&
    ln -s /opt/WhatWeb/whatweb /usr/local/bin/whatweb

# CMS Scanners

## WPScan
RUN gem install wpscan

# -----------------------------
# Instalar otras herramientas
# -----------------------------

# Enumeración de Subdominios

## Findomain
RUN wget https://github.com/Findomain/Findomain/releases/latest/download/findomain-linux.zip &&
    unzip findomain-linux.zip &&
    chmod +x findomain &&
    mv findomain /usr/local/bin/ &&
    rm findomain-linux.zip

# Escaneo de Puertos y Servicios

## Nmap
RUN apt-get update &&
    apt-get install -y nmap

# Git Tools

## shhgit
RUN git clone https://github.com/eth0izzle/shhgit.git /opt/shhgit &&
    cd /opt/shhgit &&
    go build &&
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

# Install CloudEnum (para Cloud Discovery)
RUN git clone https://github.com/initstring/cloud_enum.git /opt/cloud_enum &&
    pip3 install -r /opt/cloud_enum/requirements.txt

# Install S3Scanner (para AWS Bucket Enumeration)
RUN git clone https://github.com/sa7mon/S3Scanner.git /opt/S3Scanner &&
    pip3 install -r /opt/S3Scanner/requirements.txt

# Install GCPBucketBrute (para GCP Bucket Enumeration)
RUN git clone https://github.com/RhinoSecurityLabs/GCPBucketBrute.git /opt/GCPBucketBrute

# Install Wfuzz
RUN pip3 install wfuzz

# Instalar Flask (para la API)
RUN pip3 install flask

# Limpiar
RUN apt-get clean &&
    rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /root/

# Exponer el puerto para la API
EXPOSE 8000

# Copiar y establecer permisos para el script de entrada
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Copiar archivos de la API
COPY api /opt/api

# Comando por defecto
CMD ["/entrypoint.sh"]
