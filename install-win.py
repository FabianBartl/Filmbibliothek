
import os, sys, subprocess, custom_logger
logger = custom_logger.init(__file__, log_to_console=True)
logger.debug(f"start of script: {__file__}")

# install python packages
logger.debug("install requirements")
subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

# these packages are first available after the requirements.txt installation
import winshell, yaml
from win32com.client import Dispatch
from colorama import Fore, Back, Style, init

init(autoreset=True)
print(Fore.GREEN + "Packages installed")

# load config.yml
logger.debug("load config.yml")
with open("config.yml", "r", encoding="utf-8") as file:
	config_yaml = yaml.safe_load(file)
	logger.info("config.yml loaded")

# re-call logger with colored output since colorama is now available
logger = custom_logger.init(__file__, log_to_console=True)
logger.debug("re-call logger with colored output")

# add server-name as host to local dns resolver
name = config_yaml.get("server-name", "filmbibliothek")
logger.debug("try: add server-name as host to local dns resolver")
try:
	path = "C:\\Windows\\System32\\drivers\\etc\\hosts"
	with open(path, "r", encoding="utf-8") as file:
		content = file.read()
	with open(path, "a", encoding="utf-8") as file:
		if not f" {name}" in content:
			file.write(f"\n# host for flask webserver of '{name}' project")
			file.write(f"\n127.0.0.1 {name}\n")
	
	logger.info(f"added {name=} to local dns resolver")
	print(Fore.GREEN + f"Host '{name}' added to DNS resolver")
except PermissionError:
	logger.warning(f"PermissionError: failed to add {name=} to local dns resolver")
	print(Fore.YELLOW + f"Run the installation script as administrator to add '{name}' as host to local DNS resolver")
except Exception as error:
	logger.critical(error)
	print(error)
	exit(-1)

# add webserver.py to startup directory
logger.debug("add webserver.py to windows startup directory")
startup_path = os.path.join(winshell.startup(), f"webserver_{name}.lnk")
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
try:
	subprocess.check_call([sys.executable, "collect_metadata.py"])
except Exception as error:
	logger.error(error)
	exit()

# start webserver
logger.debug("run webserver.py")
print("Run webserver.py")
try:
	subprocess.check_call([sys.executable, "webserver.py"])
except Exception as error:
	logger.error(error)
	exit()

logger.debug(f"end of script: {__file__}")
