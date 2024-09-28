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

chmod +x entrypoint.sh

# Build the Docker image
docker build -t lemonbooster -f Dockerfile .

# Run the Docker container
docker run -d -p 8000:8000 --name lemonbooster lemonbooster

echo "LemonBooster is now running on port 8000."
