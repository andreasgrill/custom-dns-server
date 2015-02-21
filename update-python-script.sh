#!/bin/sh

## Update Custom DNS-Server python script ##

rm ./custom-dns-server.py
wget https://raw.githubusercontent.com/andreasgrill/custom-dns-server/master/custom-dns-server.py
chmod +x ./custom-dns-server.py