import requests
import socket
import time
import getpass
from bs4 import BeautifulSoup
import collections
import signal
import sys
import logging.config
import gi
gi.require_version('Notify', '0.7')
from gi.repository import Notify
import base64
import os
import json

#---URL FOR REQUESTS---#
auth_url = "https://auth5.unipi.it/auth/perfigo_cm_validate.jsp"
report_url = "https://auth5.unipi.it/auth/perfigo_report.jsp"
logout_url = "https://auth5.unipi.it/auth/perfigo_logout.jsp"

def setup_logging(
	default_path='logging.json', 
	default_level=logging.INFO,
	env_key='LOG_CFG'
):
	"""Setup logging configuration """
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

# Logging configuration
setup_logging()
logger = logging.getLogger('Auto Login UniPi')

def get_payload_login(response):
	soup = BeautifulSoup(response.text, "html.parser")

	logger.debug("Get payload for login")
	payload_dic = collections.OrderedDict()
	for element in soup.find("form").findAll("input"):
		if element.has_attr("value"):
			if element["type"] != "submit":
				payload_dic[element["name"]] = element["value"]

	return payload_dic

def get_payload_logout(response):
	soup = BeautifulSoup(response.text, "html.parser")

	logger.debug("Get payload for logout")
	payload_dic = collections.OrderedDict()
	for element in soup.findAll("form")[1].findAll("input"):
		if element.has_attr("value"):
			if element["type"] != "submit":
				payload_dic[element["name"]] = element["value"]

	return payload_dic
	
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

def logout(s,payload):
	try:
		logger.debug("Logout")
		s.get(logout_url,params={"user_key" : payload["userkey"]})
		s.post(report_url, data=payload)
	except requests.exceptions.RequestException as e:
		logger.error(e)
		Hello=Notify.Notification.new("Auto UniPi Connection", "Login problems", "dialog-information")
		Hello.show()
		sys.exit(1)
	except KeyError as e:
		logger.error(e)
		Hello=Notify.Notification.new("Auto UniPi Connection", "Logout error due to an incorrect login", "dialog-information")
		Hello.show()
		sys.exit(1)

def main():
	Notify.init("Notify Init")
	# Searching for config path
	if "-cp" not in sys.argv:
		logger.error("Config path not specified")
		sys.exit(1)
	else:
		# Reading config path
		cp = sys.argv[sys.argv.index("-cp")+1]
		# If more than one parameters has passed
		if len(sys.argv) > 3:
			# Create new user config
			if "--user-config" in sys.argv:
				username = input("Username: ")
				password = getpass.getpass()
				user_config = open(cp,"wb")
				user_config.write(base64.b64encode((username+":"+password).encode("utf-8")))
				user_config.close()
			# Delete an existing user config
			elif "--delete-user-config" in sys.argv:
				pass
		
	s = requests.Session()
	payload_logout = {}

	# Build data for login post request
	try:
		logger.debug("Get parameter")
		response_login = s.get(auth_url)
	except requests.exceptions.RequestException as e:
		logger.error(e)
		sys.exit(1)
	payload_login = get_payload_login(response_login)
	
	# Insert username and password on payload data
	try:
		user_config = open(cp,"rb")
		user_pass = user_config.read()
		user_config.close()
	except IOError as e:
		logger.error(e)
		logger.info("Run with --user-config option")
		sys.exit(1)

	decoded_user_pass = str(base64.b64decode(user_pass)).split("'")[1]
	payload_login["username"] = decoded_user_pass.split(":")[0]
	payload_login["password"] = decoded_user_pass.split(":")[1]

	def stop_handler(signal, frame):
		logout(s,payload_logout)
		logger.debug("Sigterm signal recieved")
		Hello=Notify.Notification.new("Auto UniPi Connection", "Logout", "dialog-information")
		Hello.show()
		sys.exit(0)

	signal.signal(signal.SIGTERM, stop_handler)
	signal.signal(signal.SIGINT, stop_handler)

	# Infinite loop to check internet connection
	while True:
		if internet_on() == False:
			logger.debug("Reconnection")
			Hello=Notify.Notification.new("Auto UniPi Connection", "Login successfully", "dialog-information")
			Hello.show()
			response_logout = login(payload_login,auth_url,s)
			payload_logout = get_payload_logout(response_logout)
		time.sleep(5)

# Internet connection check
def internet_on(url='https://github.com', timeout=5):
	try:
		_ = requests.head(url, timeout=timeout)
		return True
	except requests.ConnectionError:
		pass
	return False

if __name__ == "__main__":
    main()
