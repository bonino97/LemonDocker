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

# Run the Docker container with resource limits
docker run -d \
  --name lemonbooster \
  --memory="6g" \
  --memory-swap="7g" \
  --cpus=1.8 \
  --cpu-shares=1024 \
  -v $(pwd)/results:/results \
  -p 8000:8000 \
  -p 6379:6379 \
  -p 5555:5555 \
  --restart unless-stopped \
  lemonbooster

echo "LemonBooster is now running on port 8000 with the following resource limits:"
echo "- Memory: 6GB (+ 1GB swap)"
echo "- CPU: 1.8 cores"
echo "Monitor the resource usage with: docker stats lemonbooster"