#!/usr/bin/python

# Custom DNS Server
# version 0.9.1

import subprocess
import urllib2
import os.path
import re
import json

def getconfig(path):
	with open(path, 'r') as f:
		return json.load(f)

def regescape(s):
	return re.escape(s)

def dnsfixer(disableFix, config):

	uci = config['mode'] == 'uci'
	configMode = config[config['mode']]
	oldIps = []

	# get the existing dns entries
	try:
		if uci:
			entries = subprocess.check_output(["uci", "get", configMode["settingspath"]]).strip().replace(" ","\n")
		else:
			entries = subprocess.check_output(["grep", "server\\s*=\\s*\\/", configMode["dnsmasq-config-path"]])
		
		oldIps = re.findall(r"^.*?\/(?:%s)[^0-9]+([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}).*?$" % (regescape(config["domain"])), entries, re.M)
		print oldIps

	except RuntimeError as e:
		print "Error occurred while getting existing dns-server entries."
		print e

	if not disableFix:
		# load the new entries from the server repo
		response = urllib2.urlopen(config["dns-server-repo"] % (",".join(oldIps)))
		html = response.read()
	else:
		html = ""

	if len(html) > 0 or (disableFix and len(dnsentries) > 0):
		# remove old nf entries
		for ip in oldIps:
			if uci:
				subprocess.call(["uci", "del-list", '%s="/%s/%s"' % (configMode["settingspath"], config["domain"], ip)])
			else:
				subprocess.call(["sed", "-i", "/server=\\/%s\\/%s/d" % (regescape(config["domain"]), regescape(ip)), configMode["dnsmasq-config-path"]])

		# add new entries
		if not disableFix:
			for ip in html.split(","):
				ip = ip.strip()
				if not re.match('^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$', ip):
					continue
					
				if uci:
					subprocess.call(["uci", "add_list", "%s=/%s/%s" % (configMode["settingspath"], config["domain"], ip)])
				else:
					with open(configMode["dnsmasq-config-path"], "a") as myfile:
						myfile.write("server=/%s/%s\n" % (config["domain"], ip))


		# restart dnsmasqd
		for cmd in configMode["restart-dnsmasq"]:
			subprocess.call(cmd)

dnsfixer(os.path.exists("disabled"), getconfig('config.json'))
