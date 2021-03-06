import argparse
import os
import stat
import getpass
from shutil import copyfile
import shutil
import fileinput

def main():
	parser = argparse.ArgumentParser(description='Alup INSTALLER',add_help=True)
	parser.add_argument('-c', dest='config', help='Set configuration folder')
	parser.add_argument('action', choices=('install', 'remove'), help="INSTALL or REMOVE Alup")
	args = parser.parse_args()

	username = getpass.getuser()
	home = os.path.expanduser("~")
	alup_dir = home + "/.alup/"
	obj_dir = alup_dir + "obj"
	log_dir = alup_dir + "log"

	if(args.action == "install"):
		if not os.path.exists(alup_dir):
			print("Create folder " + alup_dir)
			os.makedirs(alup_dir)
		if not os.path.exists(obj_dir):
			print("Create folder " + obj_dir)
			os.makedirs(obj_dir)
		if not os.path.exists(log_dir):
			print("Create folder " + log_dir)
			os.makedirs(log_dir)

		for f in ["alup.py", "installer.py", "logging.json"]:
			print("Copying " + f + " -> " + alup_dir + f)
			copyfile(f ,alup_dir + f)

		print("Copying alup.py -> alup")
		copyfile("alup.py", "alup")
		st = os.stat("alup")
		print("Exec chmod +x alup")
		os.chmod("alup", st.st_mode | stat.S_IXOTH | stat.S_IWGRP | stat.S_IEXEC)

		with fileinput.FileInput("alup.service", inplace=True, backup='.bak') as file:
			for line in file:
				if( "user_name" in line):
					print(line.replace("user_name", username), end='')
				else:
					print(line.replace("config_path", alup_dir), end='')

		print("\nComplete by run the following as super user:")
		print("# cp alup /usr/local/bin/")
		print("If you have systemd also:")
		print("# cp alup.service /etc/systemd/system/ \n")

	elif(args.action == "remove"):
		if os.path.exists(alup_dir):
			print("Deleting " + alup_dir)
			shutil.rmtree(alup_dir)
			print("\nComplete by run as super user:")
			print("# rm /usr/local/bin/alup")
			print("If you have systemd, disable the service and:")
			print("# rm /etc/systemd/system/alup.service \n")
		else:
			print("Alup is not installed")

if __name__ == "__main__":
    main()
