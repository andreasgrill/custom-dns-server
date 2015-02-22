#!/usr/bin/python

## Update Custom DNS-Server python script ##

import urllib2
import os

def getrelpath(path):
	return "%s/%s" % (os.path.dirname(os.path.abspath(__file__)), path)

response = urllib2.urlopen('https://raw.githubusercontent.com/andreasgrill/custom-dns-server/master/custom-dns-server.py')
html = response.read()

with open(getrelpath("custom-dns-server.py"), "w") as myfile:
	myfile.write(html)
