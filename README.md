# custom-dns-server
Updates dnsmasq config to forward specific domain queries to custom DNS servers.

## Requirements
 * Python >= 2.6 with subprocess, urllib2, os, re, json libraries
 * Webservice to retrieve new DNS servers
 * Either direct access to dnsmasq.conf or [UCI][uci] support
 
 
## How it works
Updates dnsmasq configuration either with [UCI][uci] or directly, to forward specific DNS queries to DNS server specified by a [webservice](#webservice).
Profiles can be specified in [config.json](config.json) for server-specific configurations and commands.


## Webservice
A webservice is required that might take existing DNS server IPs as GET parameters and should return IP addresses separated by comma, or nothing if no change is required. The webservice and its exact URI can be specified in the `dns-server-repo` entry in the config.json file.


## Configuration
The [default.config.json](default.config.json) file contains an example configuration. Create a copy of [default.config.json](default.config.json) and name the new copy `config.json`. The entries `domain`, `dns-server-repo` and `used-profile` must be adapted.


[uci]:http://nbd.name/gitweb.cgi?p=uci.git;a=summary
