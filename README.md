# custom-dns-server
Updates dnsmasq config to forward specific domain queries to dynamic DNS servers.

## Requirements
 * Python >= 2.6 with subprocess, urllib2, os, re, json libraries
 * Webservice to retrieve new DNS servers
 * Either direct access to dnsmasq.conf or [UCI][uci] support
 
 
[uci]:http://nbd.name/gitweb.cgi?p=uci.git;a=summary
