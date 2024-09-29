# README.md

## LemonBooster: Automated Reconnaissance and Vulnerability Scanning Platform

### Description

LemonBooster is an automated platform that integrates multiple security tools for enumeration, discovery, and vulnerability scanning. This README provides detailed instructions to install and run LemonBooster on a Digital Ocean Droplet.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
   - [Quick Installation using build.sh](#quick-installation-using-buildsh)
   - [Manual Installation](#manual-installation)
3. [Included Tools](#included-tools)
4. [Using the API](#using-the-api)
   - [Example Requests](#example-requests)
5. [Security Considerations](#security-considerations)
   - [Implementing Authentication](#implementing-authentication)
   - [Configuring the Firewall](#configuring-the-firewall)
6. [Additional Notes](#additional-notes)
7. [Credits](#credits)
8. [Troubleshooting](#troubleshooting)
9. [Contact](#contact)
10. [Conclusion](#conclusion)

---

## Prerequisites

- A **Digital Ocean** account.
- A **Droplet** with **Ubuntu 22.04 (LTS)** installed.
- SSH access to the Droplet.
- SSH keys configured for secure access.
- Git installed on your local machine (to clone the repository if necessary).

---

## Installation

### Quick Installation using build.sh

We have provided a `build.sh` script located within the `install` directory of the repository. This script automates the entire installation process, including updating the system, installing dependencies, building the Docker image, and running the container.

#### **Steps:**

1. **Connect to the Droplet**

   From your local terminal, connect to your Droplet using SSH:

   ```bash
   ssh root@<DROPLET_IP>
   ```

   Replace `<DROPLET_IP>` with the public IP address of your Droplet.

2. **Clone the Repository**

   On your Droplet, clone the LemonDocker repository:

   ```bash
   git clone https://github.com/bonino97/LemonDocker.git
   ```

3. **Navigate to the Install Directory**

   ```bash
   cd LemonDocker/install
   ```

4. **Give Execution Permissions to build.sh**

   ```bash
   chmod +x build.sh
   ```

5. **Run build.sh**

   ```bash
   ./build.sh
   ```

   The `build.sh` script will perform the following actions:

   - Update the system packages.
   - Install Git and Docker.
   - Build the Docker image.
   - Run the Docker container.

6. **Verify the Container is Running**

   Check that the container is running:

   ```bash
   docker ps
   ```

   You should see output similar to:

   ```
   CONTAINER ID   IMAGE          COMMAND             CREATED          STATUS          PORTS                    NAMES
   <CONTAINER_ID> lemonbooster   "/entrypoint.sh"    xx minutes ago   Up xx minutes   0.0.0.0:8000->8000/tcp   lemonbooster
   ```

---

### Manual Installation

For users who prefer to install everything manually, follow these steps.

**Repository Structure:**

```
LemonDocker/
├── Dockerfile
├── entrypoint.sh
├── api/
│   └── server.py
├── install/
    └── build.sh
```

#### **1. Connect to the Droplet**

From your local terminal, connect to your Droplet using SSH:

```bash
ssh root@<DROPLET_IP>
```

Replace `<DROPLET_IP>` with the public IP address of your Droplet.

#### **2. Update the System and Install Dependencies**

Update system packages and install Git and Docker:

```bash
# Update the system
apt-get update && apt-get upgrade -y

# Install Git
apt-get install -y git

# Install Docker
apt-get install -y docker.io

# Start and enable Docker
systemctl start docker
systemctl enable docker
```

#### **3. Clone the Repository**

Clone the LemonDocker repository on your Droplet:

```bash
git clone https://github.com/bonino97/LemonDocker.git
cd LemonDocker
```

#### **4. Build the Docker Image**

Build the Docker image using the provided Dockerfile:

```bash
docker build -t lemonbooster -f Dockerfile .
```

This process may take several minutes, as it installs all the tools and dependencies.

#### **5. Run the Docker Container**

Start the Docker container with the following command:

```bash
docker run -d -p 8000:8000 --name lemonbooster lemonbooster
```

- `-d`: Runs the container in detached mode (in the background).
- `-p 8000:8000`: Maps port 8000 of the container to port 8000 on the host.
- `--name lemonbooster`: Names the container for easier management.

#### **6. Verify the Container is Running**

Check that the container is running:

```bash
docker ps
```

You should see output similar to:

```
CONTAINER ID   IMAGE          COMMAND             CREATED          STATUS          PORTS                    NAMES
<CONTAINER_ID> lemonbooster   "/entrypoint.sh"    xx minutes ago   Up xx minutes   0.0.0.0:8000->8000/tcp   lemonbooster
```

---

## Included Tools

LemonBooster includes a wide range of security tools categorized by their primary functions:

### Subdomain Enumeration
- [Amass](https://github.com/owasp-amass/amass)
- [Subfinder](https://github.com/projectdiscovery/subfinder)
- [ASNmap](https://github.com/projectdiscovery/asnmap)
- [Assetfinder](https://github.com/tomnomnom/assetfinder)
- [Chaos](https://github.com/projectdiscovery/chaos-client)
- [Cero](https://github.com/glebarez/cero)
- [Sublist3r](https://github.com/aboul3la/Sublist3r)
- [KnockPy](https://github.com/guelfoweb/knock)
- [Altdns](https://github.com/infosec-au/altdns)
- [Findomain](https://github.com/Findomain/Findomain)
- [GitHub Subdomains](https://github.com/gwen001/github-subdomains)

### Active Subdomain Verification
- [Httpx](https://github.com/projectdiscovery/httpx)
- [Httprobe](https://github.com/tomnomnom/httprobe)
- [Dnsx](https://github.com/projectdiscovery/dnsx)
- [MassDNS](https://github.com/blechschmidt/massdns)
- [Subrake](https://github.com/hash3liZer/Subrake)

### Spidering and Crawling
- [Gospider](https://github.com/jaeles-project/gospider)
- [Hakrawler](https://github.com/hakluke/hakrawler)
- [Katana](https://github.com/projectdiscovery/katana)

### Port and Service Scanning
- [Naabu](https://github.com/projectdiscovery/naabu)
- [Tlsx](https://github.com/projectdiscovery/tlsx)
- [Masscan](https://github.com/robertdavidgraham/masscan)
- [Nmap](https://nmap.org/)

### Technology Fingerprinting
- [Webanalyze](https://github.com/rverton/webanalyze)
- [WhatWeb](https://github.com/urbanadventurer/WhatWeb)

### Automated Vulnerability Scanning
- [Nuclei](https://github.com/projectdiscovery/nuclei)
- [Interactsh client](https://github.com/projectdiscovery/interactsh)
- [SQLMap](https://github.com/sqlmapproject/sqlmap)
- [SSLyze](https://github.com/nabla-c0d3/sslyze)
- [Nikto](https://github.com/sullo/nikto)

### Screenshots
- [GoWitness](https://github.com/sensepost/gowitness)
- [EyeWitness](https://github.com/FortyNorthSecurity/EyeWitness)

### Directory and File Brute Forcing
- [GoBuster](https://github.com/OJ/gobuster)
- [Dirsearch](https://github.com/maurosoria/dirsearch)
- [Wfuzz](https://github.com/xmendez/wfuzz)
- [Ffuf](https://github.com/ffuf/ffuf)

### CMS Scanners
- [WPScan](https://github.com/wpscanteam/wpscan)

### JavaScript Analysis
- [LinkFinder](https://github.com/GerbenJavado/LinkFinder)

### OSINT Tools
- [TheHarvester](https://github.com/laramies/theHarvester)

### Git Tools
- [shhgit](https://github.com/eth0izzle/shhgit)

### Cloud Discovery Tools
- [CloudEnum](https://github.com/initstring/cloud_enum)
- [CloudList](https://github.com/projectdiscovery/cloudlist)
- [S3Scanner](https://github.com/sa7mon/s3scanner)
- [GCPBucketBrute](https://github.com/RhinoSecurityLabs/GCPBucketBrute)

### Miscellaneous Tools
- [AlterX](https://github.com/projectdiscovery/alterx)
- [Subzy](https://github.com/PentestPad/subzy)
- [CveMap](https://github.com/projectdis

covery/cvemap)
- [uncover](https://github.com/projectdiscovery/uncover)
- [PDTM](https://github.com/projectdiscovery/pdtm)

### Wordlists
- [SecLists](https://github.com/danielmiessler/SecLists)
- [Commonspeak2-Wordlists](https://github.com/assetnote/commonspeak2-wordlists)
- [BBH-Lists](https://github.com/bonino97/BBH-Lists)
- [DirBuster Wordlists](https://github.com/daviddias/node-dirbuster)

---

## Using the API

The API is available on port `8000` of your Droplet.

### Example Requests

#### **Run Nmap**

```bash
curl -X POST http://<DROPLET_IP>:8000/run \
-H 'Content-Type: application/json' \
-d '{
    "tool": "nmap",
    "args": ["-sV", "scanme.nmap.org"]
}'
```

#### **Run Amass for Subdomain Enumeration**

```bash
curl -X POST http://<DROPLET_IP>:8000/run \
-H 'Content-Type: application/json' \
-d '{
    "tool": "amass",
    "args": ["enum", "-d", "example.com"]
}'
```

#### **Run Nuclei for Vulnerability Scanning**

```bash
curl -X POST http://<DROPLET_IP>:8000/run \
-H 'Content-Type: application/json' \
-d '{
    "tool": "nuclei",
    "args": ["-u", "https://example.com"]
}'
```

---

## Security Considerations

It is crucial to secure your API to prevent unauthorized access.

### Implementing Authentication

Modify the `api/server.py` file to include authentication using an API key.

**Step 1: Edit `server.py`**

```bash
nano api/server.py
```

**Add the following code at the beginning of the file:**

```python
API_KEY = 'YOUR_API_KEY'
```

**Modify the `run_tool()` function to include API key verification:**

```python
@app.route('/run', methods=['POST'])
def run_tool():
    api_key = request.headers.get('X-API-Key')
    if api_key != API_KEY:
        return jsonify({'error': 'Unauthorized'}), 401

    # Rest of the code...
```

**Step 2: Rebuild the Docker Image**

After modifying `server.py`, rebuild the Docker image:

```bash
docker build -t lemonbooster -f Dockerfile .
```

**Step 3: Restart the Container**

Stop and remove the previous container:

```bash
docker stop lemonbooster
docker rm lemonbooster
```

Start a new container:

```bash
docker run -d -p 8000:8000 --name lemonbooster lemonbooster
```

**Step 4: Send Authenticated Requests**

Include the `X-API-Key` header in your requests:

```bash
curl -X POST http://<DROPLET_IP>:8000/run \
-H 'Content-Type: application/json' \
-H 'X-API-Key: YOUR_API_KEY' \
-d '{
    "tool": "nuclei",
    "args": ["-u", "https://example.com"]
}'
```

### Configuring the Firewall

Use `ufw` to restrict access to port 8000:

```bash
# Install ufw if not already installed
apt-get install -y ufw

# Allow SSH
ufw allow ssh

# Allow access to port 8000 only from your IP
ufw allow from <YOUR_IP> to any port 8000

# Enable ufw
ufw enable
```

Replace `<YOUR_IP>` with the IP address from which you will access the API.

---

## Additional Notes

- **Tool Updates**: To update the tools within the container, update the `Dockerfile` and rebuild the image.
- **Limitations**: Ensure you have the appropriate permission before scanning domains or systems that you do not own.
- **Security**: Never expose the API without authentication in production environments.

---

## Credits

- **Author**: [Bonino97](https://github.com/bonino97)
- **Repository**: [GitHub - bonino97/LemonDocker](https://github.com/bonino97/LemonDocker)
- **License**: MIT

---

## Troubleshooting

- **Container Not Running**: Check the container logs with `docker logs lemonbooster` to identify potential errors.
- **Cannot Access the API**: Ensure that port 8000 is open and the firewall is configured correctly.
- **Authentication Error**: Verify that you are sending the `X-API-Key` header with the correct key.

---

**Note**: Always respect applicable laws and regulations when performing security testing and vulnerability scans. Obtain proper authorization before scanning systems or networks that you do not own.

---

### Appendix: build.sh Script

The `build.sh` script is located in the `install` directory of the repository. It automates the installation process.

#### build.sh

```bash
#!/bin/bash

# Update system and install dependencies
apt-get update && apt-get upgrade -y

# Install Git
apt-get install -y git

# Install Docker
apt-get install -y docker.io

# Start and enable Docker
systemctl start docker
systemctl enable docker

# Navigate to the repository root
cd ..

# Build the Docker image
docker build -t lemonbooster -f Dockerfile .

# Run the Docker container
docker run -d -p 8000:8000 --name lemonbooster lemonbooster

echo "LemonBooster is now running on port 8000."
```

**Notes:**

- The `build.sh` script assumes that you are in the `install` directory, and the `Dockerfile` is in the parent directory.
- It updates the system, installs Git and Docker, builds the Docker image, and runs the container.

---