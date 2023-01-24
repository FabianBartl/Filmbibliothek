
import os, sys, subprocess, custom_logger
logger = custom_logger.init(__file__)
logger.debug(f"start of script: {__file__}")

# install python packages
logger.debug("install requirements")
with open("requirements.txt", "r", encoding="utf-8") as file:
	requirements = [ line.strip() for line in file.readlines() ]
for package in requirements:
	if not package in sys.modules:
		logger.info(f"install {package=}")
		subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# these packages are first available after the requirements.txt installation
import winshell, yaml
from win32com.client import Dispatch
from colorama import Fore, Back, Style, init

init(autoreset=True)
print(Fore.GREEN + "Packages installed")

# re-call logger with colored output since colorama is now available 
logger = custom_logger.init(__file__)
logger.debug("re-call logger with colored output")

# load config.yml
logger.debug("load config.yml")
with open("config.yml", "r", encoding="utf-8") as file:
	config_yaml = yaml.safe_load(file)
	logger.info("config.yml loaded")

# add host if server-name is not set to 0.0.0.0
host = config_yaml.get("server-host", "filmbibliothek")
logger.debug("try: add host to local dns resolver")
customHost = False
try:
	with open("C:\\Windows\\System32\\drivers\\etc\\hosts", "r", encoding="utf-8") as file:
		content = file.read()
	with open("C:\\Windows\\System32\\drivers\\etc\\hosts", "a", encoding="utf-8") as file:
		if not host in content:
			file.write(f"\n# host for flask webserver of '{host}' project")
			file.write(f"\n127.0.0.1    {host}\n")
	
	customHost = True
	logger.info(f"added {host=} to local dns resolver")
	print(Fore.GREEN + f"Host '{host}' added to DNS resolver")
except PermissionError:
	logger.warning(f"PermissionError: failed to add {host=} to local dns resolver")
	print(Fore.YELLOW + f"Run the installation script as administrator to add '{host}' as host to local DNS resolver")
except Exception as error:
	logger.critical(error)
	print(error)
	exit()

# add webserver.py to startup directory
logger.debug("add webserver.py to windows startup directory")
startup_path = os.path.join(winshell.startup(), f"webserver_{host}.lnk")
target_path = os.path.abspath(os.path.join(os.path.curdir, "webserver.py"))
working_dir = os.path.abspath(os.path.curdir)
logger.debug(f"{startup_path=} {target_path=} {working_dir=}")

shell = Dispatch("WScript.shell")
shortcut = shell.CreateShortCut(startup_path)
shortcut.Targetpath = target_path
shortcut.WorkingDirectory = working_dir
shortcut.save()
logger.info("added webserver.py to windows startup directory")
print(Fore.GREEN + "Webserver script added to windows startup directory")

# collect metadata
subprocess.check_call([sys.executable, "collect_metadata.py"])

# start webserver
logger.debug("run webserver.py")
print("Run webserver.py")
subprocess.check_call([sys.executable, "webserver.py"])

logger.debug(f"end of script: {__file__}")
