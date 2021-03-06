#!/bin/bash
# UBUNTU
set -e
# Prepare VM

# Docker and other required packages
apt-get update
sleep 2
apt-get install -y ca-certificates curl unzip gnupg lsb-release
mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list >/dev/null
apt-get update
sleep 2
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Docker compose
curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
docker-compose --version

# Install HidlRoute
cd "/opt" || exit
curl -fsSL https://get.hidlroute.org >/tmp/hidlroute-install.sh
chmod +x /tmp/hidlroute-install.sh
/tmp/hidlroute-install.sh
sleep 2

# Add hidlroute to autostart
echo "Registering HidlRoute in autostart"
systemctl enable hidlroute
echo "  DONE"

# Start hidlroute stack
echo "Bootstrapping docker containers"
hidlroute-compose up -d
echo ""
echo "DONE: Docker containers bootstrapped and launched"
sleep 3

# Apply migrations
echo "Applying migrations"
hidlmng migrate
echo "DONE: Migrations applied"

echo "Loading initial data"
hidlmng create-default-super-group
echo "DONE: Initial data loaded"

# Create superuser
if [ -z "$HIDL_SUPERUSER_LOGIN" ]; then
  # if config vars are not set - run interactive setup
  hidlmng createsuperuser
else
  if [ -z "$HIDL_SUPERUSER_EMAIL" ]; then
    HIDL_SUPERUSER_EMAIL="$HIDL_SUPERUSER_LOGIN@fakemail.com"
  fi
  hidlmng createsuperuser --username="$HIDL_SUPERUSER_LOGIN" --email="$HIDL_SUPERUSER_EMAIL" --no-input
fi

echo "Shutting down HidlRoute stack"
hidlroute-compose stop
echo "Starting HidlRoute service"
systemctl start hidlroute

echo
echo "DEPLOYMENT IS COMPLETED SUCCESSFULLY"
echo
