#!/usr/bin/env python3

import requests
import socket
import time
import getpass
from bs4 import BeautifulSoup
import collections
import signal
import sys
import logging.config
import base64
import os
import json
from os.path import expanduser
import pickle
import argparse
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Disable request warning caused by URL forwarding to captive portal page
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

#---JSP FOR REQUESTS---#
auth_url = "auth/perfigo_cm_validate.jsp"
report_url = "auth/perfigo_report.jsp"
logout_url = "auth/perfigo_logout.jsp"

work_directory = ""
logger = ""

payload_logout_fname = "obj/payload_logout.pkl"
credentials_fname = ".alup_user.conf"

# Load loging configuration from json file
def setup_logging(
	default_path=work_directory + 'logging.json', default_level=logging.INFO, env_key='LOG_CFG'):
	print(work_directory)
	path = default_path
	value = os.getenv(env_key, None)
	if value:
		path = value
	if os.path.exists(path):
		with open(path, 'rt') as f:
			config = json.load(f)
		logging.config.dictConfig(config)
	else:
		logging.basicConfig(level=default_level)

# Get submit login from web page
def get_payload_login(response):
	soup = BeautifulSoup(response.text, "html.parser")

	logger.debug("Get payload for login")
	payload_dic = collections.OrderedDict()
	for element in soup.find("form").findAll("input"):
		if element.has_attr("value"):
			if element["type"] != "submit":
				payload_dic[element["name"]] = element["value"]

	return payload_dic

# Get submit logout from web page
def get_payload_logout(response):
	soup = BeautifulSoup(response.text, "html.parser")

	logger.debug("Get payload for logout")
	payload_dic = collections.OrderedDict()
	for element in soup.findAll("form")[1].findAll("input"):
		if element.has_attr("value"):
			if element["type"] != "submit":
				payload_dic[element["name"]] = element["value"]

	return payload_dic

# Make submit login
def login(payload,url,s):
	try:
		logger.debug("Login")
		response = s.post(url, data=payload)
		if "Unknown user" in response.text:
			logger.error("Unknown User")
		elif "Invalid username or password" in response.text:
			logger.error("Invalid username or password")
	except requests.exceptions.RequestException as e:
		logger.error(e)
		sys.exit(1)

	return response

# Make submit logout
def logout(s,payload):
	try:
		logger.debug("Logout")
		domain_url = payload["domain"]

		# Deleting domain element before sending
		del payload["domain"]

		s.get(domain_url + logout_url, params={"user_key" : payload["userkey"]})
		s.post(domain_url + report_url, data=payload)
		if(os.path.exists(work_directory + payload_logout_fname)):
			os.remove(work_directory + payload_logout_fname)
	except requests.exceptions.RequestException as e:
		logger.error(e)
		sys.exit(1)
	except KeyError as e:
		logger.error(e)
		sys.exit(1)

# Internet connection check
def internet_on(url='https://github.com', timeout=10):
	try:
		_ = requests.head(url, timeout=timeout)
		return True
	except requests.ConnectionError:
		logger.debug("Exception: Connection Error")
		pass
	except requests.Timeout:
		logger.debug("Exception: Timeout")
		pass
	except Exception:
		logger.debug("Exception: Generic")
		pass
	return False

# Read and decrypt username and password from file
# cp - path of file containing credential
def get_credential(cp):
	try:
		user_config = open(cp,"rb")
		user_pass = user_config.read()
		user_config.close()
	except IOError as e:
		logger.error(e)
		logger.info("Run with --user-config option")
		sys.exit(1)

	# Decrypting username and password with base64
	decoded_user_pass = str(base64.b64decode(user_pass)).split("'")[1]
	u = decoded_user_pass.split(":")[0]
	p = decoded_user_pass.split(":")[1]

	return u,p

# Serialize a object
def save_obj(obj, name):
	with open(work_directory + 'obj/'+ name + '.pkl', 'wb') as f:
		pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

# Deserialize a object
def load_obj(fname):
	with open(fname, 'rb') as f:
		return pickle.load(f)

# Check UniPi domain by searching for Serra web login page
def is_unipi():
	try:
		s = requests.get("https://github.com",verify=False)
	except requests.ConnectionError:
		logger.debug("Exception is_unipi: Connection Error")
		return False
	return "auth" in s.text

# Get domain for login and logout
def get_auth_domain():
	try:
		s = requests.get("https://github.com",verify=False)
	except requests.ConnectionError:
		logger.debug("Exception is_unipi: Connection Error")
		return False
	while True:
		logger.debug("Trying to get auth URL domain...")
		if "auth" in s.text:
			return s.text.split("URL")[1].split("=")[1].split("auth/")[0]
		time.sleep(2)

def main():
	parser = argparse.ArgumentParser(description='Automatic Login for University of Pisa (Captive Portal)',add_help=True)
	group = parser.add_mutually_exclusive_group(required=False)
	group.add_argument('--new-profile',dest='new',action='store_true', help='Create a new user login profile')
	group.add_argument('--delete-profile',dest='delete',action='store_true', help='Delete existing user profile')
	parser.add_argument('-c', dest='config', required=True, help='Path to configuration folder')
	args = parser.parse_args()

	# Logging configuration
	global work_directory
	work_directory = args.config
	setup_logging()
	# Check if alup work directory exists
	if os.path.isdir(work_directory) == False:
		# !!This should be an error log messages!!
		print("Configuration folder not found")
		sys.exit(1)

	global logger
	logger = logging.getLogger('Auto Login UniPi')

	# Create a new user login profile
	if args.new :
		username = input("Username: ")
		password = getpass.getpass()
		user_config = open(work_directory + credentials_fname, "wb")
		user_config.write(base64.b64encode((username+":"+password).encode("utf-8")))
		user_config.close()
	# Delete an existing user login profile
	elif args.delete :
		pass

	s = requests.Session()

	payload_logout = {}
	# Check if exist a payload object serialezed
	# Sometimes it's due to an incorrect logout
	if(os.path.isfile(work_directory + payload_logout_fname)):
		payload_logout = load_obj(work_directory + payload_logout_fname)

	def stop_handler(signal, frame):
		logout(s,payload_logout)
		logger.debug("Sigterm/Sigint signal recieved")
		sys.exit(0)

	signal.signal(signal.SIGTERM, stop_handler)
	signal.signal(signal.SIGINT, stop_handler)

	# Infinite loop to check internet connection
	while True:
		# Make reconnection if internet connection is down and the domain is UniPi
		if internet_on() == False and is_unipi():
			logger.debug("Reconnection")
			domain_url = get_auth_domain()
			response_login = s.get(domain_url + auth_url)

			# Login
			payload_login = get_payload_login(response_login)
			payload_login["username"],payload_login["password"] = get_credential(work_directory + credentials_fname)

			# Payload Logout and serialization
			response_logout = login(payload_login,domain_url + auth_url,s)
			payload_logout = get_payload_logout(response_logout)
			# Saving domain in payload for logout
			payload_logout["domain"] = domain_url
			save_obj(payload_logout,"payload_logout")
		time.sleep(5)

if __name__ == "__main__":
    main()
