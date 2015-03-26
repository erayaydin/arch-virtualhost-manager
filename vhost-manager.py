#!/usr/bin/python

import getopt, sys, os, shutil

def main(argv):
	mode     = ''
	name     = ''
	public   = 'public_html'
	composer = None
	git      = False
	try:
		opts, args = getopt.getopt(argv, "hm:n:p:c:g", ["mod=", "name=", "public=", "composer="])
	except getopt.GetoptError:
		print("test.py -m <mode> -n <name> [-p <public_html> -c <composer-project>] -g")
		sys.exit(2)

	for opt, arg in opts:
		if opt == "-h":
			print("test.py -m <mode> -n <name> [-p <public_html> -c <composer-project> -g]")
			sys.exit()
		elif opt in ("-m", "--mod"):
			mode = arg
		elif opt in ("-n", "--name"):
			name = arg
		elif opt in ("-p", "--public"):
			public = arg
		elif opt in ("-c", "--composer"):
			composer = arg
		elif opt in ("-g", "--git"):
			git = True

	if mode in ("add", "a"):
		if(not(composer is None)):
			print("Create {0} project from composer...".format(composer))
			os.system("composer create-project {1} /srv/http/{0}".format(name, composer))

		if(os.path.exists("/srv/http/{0}".format(name))):
			print("Project folder already exists!")
		else:
			print("Creating project folder...")
			os.mkdir("/srv/http/{0}".format(name))

		if(os.path.exists("/srv/http/{0}/{1}".format(name, public))):
			print("public_html folder already exists!")
		else:
			print("Creating "+public+" folder...")
			os.mkdir("/srv/http/{0}/{1}".format(name, public))

		if(git):
			os.system("git init /srv/http/{0}".format(name))

		if(os.path.exists("/etc/httpd/conf/vhosts/{0}.conf".format(name))):
			print("virtual host file already exists!")
		else:
			print("Creating virtual host file...")
			vhostfile = open("/etc/httpd/conf/vhosts/{0}.conf".format(name), "w+")
			hostConf = "<VirtualHost *:80>\nServerAdmin webmaster@{0}\nDocumentRoot \"/srv/http/{0}/{1}\"\nServerName {0}\nServerAlias www.{0}\nErrorLog \"/var/log/httpd/{0}-error log\"\nCustomLog \"/var/log/httpd/{0}-access log\" common\n</VirtualHost>"
			vhostfile.write(hostConf.format(name, public))
			vhostfile.close()

		print("Adding to hosts file...")
		hostsfile = open("/etc/hosts", "a")
		hostsFileText = "\n127.0.0.1 {0} www.{0}"
		hostsfile.write(hostsFileText.format(name))
		hostsfile.close()

		print("Restarting httpd service...")
		os.system("systemctl restart httpd")

	elif mode in ("remove", "r"):
		print("Removing project folder...")
		shutil.rmtree("/srv/http".format(name))

		if(os.path.exists("/etc/httpd/conf/vhosts/{0}.conf".format(name))):
			print("Removing virtual host file...")
			os.remove("/etc/httpd/conf/vhosts/{0}.conf".format(name))
		else:
			print("Virtual host file doesn't exists!")

	elif mode in ("install", "i"):
		print("Installing...")

		httpdFile       = open("/etc/hosts", "a")
		includeOptional = "IncludeOptional conf/vhosts/*.conf"
		httpdFile.write(includeOptional)
		httpdFile.close()

		if(not os.path.exists("/etc/httpd/conf/vhosts")):
			os.mkdir("/etc/httpd/conf/vhosts")

	print("DONE!")

if __name__ == "__main__":
	main(sys.argv[1:])