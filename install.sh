#!/bin/sh

clear
echo " ================================================================= "
echo "|  Blue Team Training Cockpit Toolkit - Install Script            |"
echo "|  by Brian L. Donaldson, Densu Labs (support@densulabs.io)        |"
echo " ================================================================= "


if [ "$(id -u)" != "0" ]; then
   echo "\n\n\033[1;31m[-]\033[1;m This installation script must be run with root (or sudo) privileges.\n"
   exit 1
fi

echo "\n\n\033[1;34m[*]\033[1;m Installing dependencies...\n"
sleep 1
apt-get update && apt-get install -y python3.8 openssl python-scapy python-ipcalc python-six
python3.8 ./BTTCPT.py install
sleep 1
echo "\n\n\033[1;34m[*]\033[1;m Creating folders..."
sleep 1
if [ ! -d "certs" ]; then
    mkdir certs
    echo "\033[1;32m[+]\033[1;m Directory 'certs' successfully created."

else
    echo "\033[1;32m[+]\033[1;m Directory 'certs' already exists."
fi

cd certs

echo "\n\n\033[1;34m[*]\033[1;m Generating server key and certificate...\n"
sleep 1
openssl req -nodes -new -x509 -days 3650 -keyout server.key -out server.crt

echo "\n\n\033[1;34m[*]\033[1;m Generating PEM..."
sleep 1
cat server.crt server.key > server.pem
echo "\033[1;32m[+]\033[1;m Certificate successfully generated."

cd ..
echo "\n\033[1;34m[*]\033[1;m Assigning ownership and permissions to files..."
chown root:root -R $(pwd)
chmod 755 -R $(pwd)
chmod 755 -R $(pwd)/*

echo "\n\033[1;32m[+]\033[1;m Installation completed!\n"