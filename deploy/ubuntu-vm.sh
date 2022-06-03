#!/bin/bash
# UBUNTU
set -e
# Prepare VM

# Docker and other required packages
apt-get update
apt-get install -y ca-certificates curl unzip gnupg lsb-release
mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Docker compose
curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
docker-compose --version

# Install HidlRoute
cd "/opt" || exit
curl -fsSL https://get.hidlroute.org > /tmp/hidlroute-install.sh
chmod +x /tmp/hidlroute-install.sh
/tmp/hidlroute-install.sh

# Start hidlroute stack
hidlroute-compose up -d
# Apply migrations
hidlmng migrate

# Create superuser
hidlmng createsuperuser