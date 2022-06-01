#!/bin/bash

TEMPLATE_URL="https://github.com/HidlRoute/hidlroute-server/releases/latest/download/hidlroute-template.zip"
BASE_DIR=$(readlink -f "$(pwd)")
PROJECT_DIR_NAME="hidlroute"

COLOR_RED="\033[0;31m"
COLOR_NC="\033[0m"

generate_password() {
  tr -cd '[:alnum:]' </dev/urandom | fold -w30 | head -n1
}

generate_passwords_for_file() {
  file=$1
  search_term="@RANDOM_PWD"
  while grep -q -F "$search_term" "$file"; do
    new_passwd=$(generate_password)
    sed -i "0,/$search_term/{s//$new_passwd/}" "$file"
  done
}

ensure_dependencies_installed() {
  DEPS=("docker" "docker-compose" "curl" "sed")
  for d in "${DEPS[@]}"; do
    if [ -n "$(which "$d")" ]; then
      printf "   %-25s: installed\n" $d
    else
      printf "   %-25s: %b\n" $d "${COLOR_RED}NOT INSTALLED${COLOR_NC}"
      exit 1
    fi
  done
}

print_error() {
  msg=$1
  echo
  echo -e "${COLOR_RED}ERROR: ${msg}${COLOR_NC}"
  echo
}

if [[ $EUID -ne 0 ]]; then
  print_error "This script must be run as root"
  exit 2
fi

set -e

echo "Verifying dependencies..."
ensure_dependencies_installed
echo "OK. All dependencies installed."

if [ -d "$BASE_DIR/$PROJECT_DIR_NAME" ]; then
  print_error "Directory \"$PROJECT_DIR_NAME\" already exists at $BASE_DIR. Please remove it first or choose another location for HidlRoute installation."
  exit 3
fi

echo "Downloading data template at $BASE_DIR"
curl -Lo t.zip $TEMPLATE_URL && unzip -q t.zip && rm t.zip
BASE_DIR="$BASE_DIR/$PROJECT_DIR_NAME"
echo "Template deployed"
echo "Base dir is set to $BASE_DIR"

echo "Generating passwords..."
generate_passwords_for_file $BASE_DIR/.env
generate_passwords_for_file $BASE_DIR/.hidl.env
echo "Passwords generated"

exit 0

echo "Registering executables..."
ln -s $BASE_DIR/bin/hidlroute-compose /usr/bin/hidlroute-compose
printf "\t hidlroute-compose: /usr/bin/hidlroute-compose\n"
ln -s $BASE_DIR/bin/hidlmng /usr/bin/hidlmng
printf "\t hidlmng: /usr/bin/hidlmng\n"
echo "Executables registered"

if [ -n "$(which systemd)" ]; then
  echo "Registering systemd service"
  cp $BASE_DIR/hidlroute.service.template /etc/systemd/system/hidlroute.service
  sed -i s/-BASE_DIR-/$BASE_DIR/ /etc/systemd/system/hidlroute.service
  systemctl daemon-reload
  echo "Systemd service registered"
  echo ""
  echo "DO NOT FORGET TO ADD HIDLROUTE TO AUTOSTART WHEN YOU READY:"
  echo ""
  echo "systemctl enable hidlroute"
fi
rm $BASE_DIR/hidlroute.service.template
