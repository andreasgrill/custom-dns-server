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

def customdns(disabled, config):

	profileName = config['used-profile']
	profile = config['profiles'][profileName]
	uci = profile['mode'] == 'uci'

	oldIps = []

	# get the existing dns entries
	try:
		if uci:
			entries = subprocess.check_output(["uci", "get", profile["settingspath"]]).strip().replace(" ","\n")
		else:
			entries = subprocess.check_output(["grep", "server\\s*=\\s*\\/", profile["dnsmasq-config-path"]])
		
		oldIps = re.findall(r"^.*?\/(?:%s)[^0-9]+([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}).*?$" % (re.escape(config["domain"])), entries, re.M)

	except RuntimeError as e:
		print "Error occurred while getting existing dns-server entries."
		print e

	if not disabled:
		# load the new entries from the server repo
		response = urllib2.urlopen(config["dns-server-repo"] % (",".join(oldIps)))
		html = response.read()
	else:
		html = ""

	if len(html) > 0 or (disabled and len(dnsentries) > 0):
		# remove old nf entries
		for ip in oldIps:
			if uci:
				subprocess.call(["uci", "del-list", '%s="/%s/%s"' % (profile["settingspath"], config["domain"], ip)])
			else:
				subprocess.call(["sed", "-i", "/server=\\/%s\\/%s/d" % (re.escape(config["domain"]), re.escape(ip)), profile["dnsmasq-config-path"]])

		# add new entries
		if not disabled:
			for ip in html.split(","):
				ip = ip.strip()
				if not re.match('^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$', ip):
					continue
					
				if uci:
					subprocess.call(["uci", "add_list", "%s=/%s/%s" % (profile["settingspath"], config["domain"], ip)])
				else:
					with open(profile["dnsmasq-config-path"], "a") as myfile:
						myfile.write("server=/%s/%s\n" % (config["domain"], ip))


		# restart dnsmasqd
		for cmd in profile["restart-dnsmasq"]:
			subprocess.call(cmd)

customdns(os.path.exists("disabled"), getconfig('config.json'))
