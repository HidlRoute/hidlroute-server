#!/bin/bash
#    Hidl Route - opensource vpn management system
#    Copyright (C) 2023 Dmitry Berezovsky, Alexander Cherednichenko
#
#    Hidl Route is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Hidl Route is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

TEMPLATE_URL="https://github.com/HidlRoute/hidlroute-server/releases/latest/download/hidlroute-template.zip"
BASE_DIR=$(readlink -f "$(pwd)")
PROJECT_DIR_NAME="hidlroute"

COLOR_RED="\033[0;31m"
COLOR_YEL="\033[1;33m"
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

set_letsencrypt_email() {
  email=$1
  file=$2
  sed -i "s/LETSENCRYPT_EMAIL=/LETSENCRYPT_EMAIL=$email/" "$file"
}

set_proxy_mode() {
  proxy_mode=$1
  file=$2
  search_term="@PROXY_MODE"
  sed -i "s/$search_term/$proxy_mode/" "$file"
}

set_primary_domain() {
  domain=$1
  file=$2
  search_term="@PRIMARY_DOMAIN"
  sed -i "s/$search_term/$domain/" "$file"
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

print_warn() {
  msg=$1
  echo
  echo -e "${COLOR_YEL}WARN: ${msg}${COLOR_NC}"
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

echo
echo "Configuring HTTPS for HidlRoute web interface."
echo "The default and recommended approach is to use Let's Encrypt certificates.
Please type in the email to be associated with generated certificates."
read -p "Let's Encrypt Email [empty - to disable https]: " letsencrypt_email

if [ -z "$letsencrypt_email" ]; then
  echo "Let's encrypt email is not set. HTTPS will be disabled, you have to configure static certificates manually."
  set_proxy_mode "proxy-nohttps" $BASE_DIR/bin/hidlroute-compose
else
  set_letsencrypt_email $letsencrypt_email $BASE_DIR/.env
  set_proxy_mode "proxy-letsencrypt" $BASE_DIR/bin/hidlroute-compose
fi
echo

echo
echo "Configuring access to the web interface"
read -p "Primary public domain (e.g. vpn.mysite.com): " primary_domain
if [ -z "$primary_domain" ]; then
  print_warn "Primary domain is set to localhost. This effectively prevents normal access to the web interface from Internet."
  primary_domain=localhost
fi
set_primary_domain $primary_domain $BASE_DIR/.env
set_primary_domain $primary_domain $BASE_DIR/.hidl.env
echo

echo "Registering executables..."
ln -s $BASE_DIR/bin/hidlroute-compose /usr/bin/hidlroute-compose
printf "\t hidlroute-compose: /usr/bin/hidlroute-compose\n"
ln -s $BASE_DIR/bin/hidlmng /usr/bin/hidlmng
printf "\t hidlmng: /usr/bin/hidlmng\n"
echo "Executables registered"
echo

if [ -n "$(which systemd)" ]; then
  echo "Registering systemd service"
  cp $BASE_DIR/hidlroute.service.template /etc/systemd/system/hidlroute.service
  sed -i s/@BASE_DIR/$BASE_DIR/ /etc/systemd/system/hidlroute.service
  systemctl daemon-reload
  echo "Systemd service registered"
  echo ""
  echo "DO NOT FORGET TO ADD HIDLROUTE TO AUTOSTART WHEN YOU READY:"
  echo ""
  echo "systemctl enable hidlroute"
fi
rm $BASE_DIR/hidlroute.service.template
echo
echo "Setup completed"
echo
