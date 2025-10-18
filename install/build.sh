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

# Detect system resources
TOTAL_CPUS=$(nproc)
TOTAL_MEM_GB=$(free -g | awk '/^Mem:/{print $2}')

# Calculate resource limits adaptively
# Use 90% of available CPUs, but cap at available cores
CPU_LIMIT=$(awk "BEGIN {printf \"%.2f\", $TOTAL_CPUS * 0.9}")
# If only 1 CPU, use 0.9 to stay within limits
if (( $(echo "$CPU_LIMIT > $TOTAL_CPUS" | bc -l) )); then
  CPU_LIMIT=$TOTAL_CPUS
fi

# Use 75% of available memory, minimum 2GB
MEM_LIMIT=$(awk "BEGIN {mem=$TOTAL_MEM_GB * 0.75; if(mem < 2) mem=2; printf \"%.0fg\", mem}")
MEM_SWAP=$(awk "BEGIN {mem=$TOTAL_MEM_GB * 0.75 + 1; if(mem < 3) mem=3; printf \"%.0fg\", mem}")

echo "Detected system resources:"
echo "- CPUs: $TOTAL_CPUS"
echo "- Memory: ${TOTAL_MEM_GB}GB"
echo ""
echo "Configuring container with:"
echo "- CPU limit: $CPU_LIMIT cores"
echo "- Memory limit: $MEM_LIMIT (+ swap: $MEM_SWAP)"
echo ""

# Run the Docker container with adaptive resource limits
docker run -d \
  --name lemonbooster \
  --memory="$MEM_LIMIT" \
  --memory-swap="$MEM_SWAP" \
  --cpus=$CPU_LIMIT \
  --cpu-shares=1024 \
  -v $(pwd)/results:/results \
  -p 8000:8000 \
  -p 6379:6379 \
  -p 5555:5555 \
  --restart unless-stopped \
  lemonbooster

echo ""
echo "✅ LemonBooster is now running on port 8000 with the following resource limits:"
echo "- Memory: $MEM_LIMIT (+ $(echo $MEM_SWAP | sed 's/g//') swap)"
echo "- CPU: $CPU_LIMIT cores"
echo ""
echo "Monitor the resource usage with: docker stats lemonbooster"