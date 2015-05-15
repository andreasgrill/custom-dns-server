#!/opt/bin/python

# Custom DNS Server
# version 0.9.5

import subprocess
import urllib2
import os.path
import re
import json
from optparse import OptionParser


def getconfig(path):
	with open(path, 'r') as f:
		return json.load(f)

def getrelpath(path):
	return "%s/%s" % (os.path.dirname(os.path.abspath(__file__)), path)

def customdns(disabled, config):
	if disabled:
		print("Disabling service")
	else:
		print("Enabling service")

	profileName = config['used-profile']
	profile = config['profiles'][profileName]
	uci = profile['mode'] == 'uci'

	# get the existing dns entries
	try:
		if uci:
			entries = subprocess.check_output(["uci", "get", profile["settingspath"]]).strip().replace(" ","\n")
		else:
			entries = subprocess.check_output(["grep", "server\\s*=\\s*\\/", profile["dnsmasq-config-path"]])
		
		oldIps = re.findall(r"^.*?\/(?:%s)[^0-9]+([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}).*?$" % (re.escape(config["domain"])), entries, re.M)

	except:
		oldIps = []

	if not disabled:
		# load the new entries from the server repo
		response = urllib2.urlopen(config["dns-server-repo"].format(oldIps=",".join(oldIps), domain=config["domain"]))
		html = response.read()
	else:
		html = ""

	if len(html) > 0 or (disabled and len(oldIps) > 0):
		# remove old nf entries
		for ip in oldIps:
			if uci:
				subprocess.call("uci del_list %s=\"/%s/%s\"" % (profile["settingspath"], config["domain"], ip), shell=True)
			else:
				subprocess.call(["sed", "-i", "/server=\\/%s\\/%s/d" % (re.escape(config["domain"]), re.escape(ip)), profile["dnsmasq-config-path"]])

		# add new entries
		if not disabled:
			for ip in html.split(","):
				ip = ip.strip()
				if not re.match('^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$', ip):
					continue
					
				if uci:
					subprocess.call("uci add_list %s=\"/%s/%s\"" % (profile["settingspath"], config["domain"], ip), shell=True)
				else:
					with open(profile["dnsmasq-config-path"], "a") as myfile:
						myfile.write("server=/%s/%s\n" % (config["domain"], ip))


		# restart dnsmasqd
		for cmd in profile["restart-dnsmasq"]:
			subprocess.call(list(map(lambda x: x.format(config=profile["dnsmasq-config-path"]), cmd)))

if __name__ == "__main__":
	parser = OptionParser()                                                                                                                 
                                                                                                                                               
	parser.add_option("-s" , "--stop", action="store_true",                                                                                   
                      dest="stop", default=False,                                                                                              
                      help="Stop the service, run with default dns settings")                                                                  
                                                                                                                                               
	(opts,args) = parser.parse_args()
	customdns(opts.stop or os.path.exists(getrelpath("disabled")), getconfig("/opt/custom-dns-server/config.json"))
