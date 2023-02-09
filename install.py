
import custom_logger
logger = custom_logger.init(__file__, log_to_console=True)
logger.debug(f"start of script: {__file__}")

import os, sys, subprocess
from os.path import abspath
from os.path import join as joinpath

# install python packages
logger.debug("install requirements")
subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

# these packages are first available after the requirements.txt installation
import yaml
from colorama import Fore, Back, Style, init
# needs a script restart after the installation
try:
	import winshell
	from win32com.client import Dispatch
except ModuleNotFoundError:
	logger.error("the package 'winshell' or 'win32com' could not be imported", exc_info=True)
	logger.debug("re-call the installation script")
	subprocess.check_call([sys.executable, "install.py"])
	exit(1)
except Exception as error:
	logger.critical("UnexpectedError: the package 'winshell' or 'win32com' could not be imported", exc_info=True)
	exit(2)

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
# for windows
if sys.platform == "win32":
	logger.debug("routine for win32")
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
		logger.warning(f"PermissionError: failed to add {name=} to local dns resolver", exc_info=True)
		print(Fore.YELLOW + f"Run the installation script as administrator to add '{name}' as host to local DNS resolver")
	except Exception:
		logger.critical("UnexpectedError:", exc_info=True)
		exit(3)
# unsupported systems
else:
	logger.warning(f"failed to add {name=} to local dns resolver; your '{sys.platform}' system is not supported")
	print(Fore.YELLOW + f"failed to add {name=} to local dns resolver; your '{sys.platform}' system is not supported")

# add webserver.py to startup directory / script
logger.debug("try: add webserver.py to startup directory / script")
# for windows
if sys.platform == "win32":
	startup_path = joinpath(winshell.startup(), f"webserver_{name}.lnk")
	target_path = abspath(joinpath(os.path.curdir, "webserver.py"))
	working_dir = abspath(os.path.curdir)
	logger.debug(f"{startup_path=} {target_path=} {working_dir=}")

	shell = Dispatch("WScript.shell")
	shortcut = shell.CreateShortCut(startup_path)
	shortcut.Targetpath = target_path
	shortcut.WorkingDirectory = working_dir
	shortcut.save()
	logger.info("added webserver.py to windows startup directory")
	print(Fore.GREEN + "Webserver script added to windows startup directory")
# for linux (not tested)
elif sys.platform == "linux":
	logger.debug("routine for linux")
	try:
		path = "~/.bashrc"
		target_path = abspath(joinpath(os.path.curdir, "webserver.py"))
		with open(path, "r", encoding="utf-8") as file:
			content = file.read()
		with open(path, "a", encoding="utf-8") as file:
			if not target_path in content:
				file.write(f"\n# start flask webserver of '{name}' project")
				file.write(f"\npython3 '{target_path}'\n")
		
		logger.info(f"added '{target_path}' to ~/.bashrc")
		print(Fore.GREEN + "Webserver script added to linux ~/.bashrc")
	except PermissionError:
		logger.warning(f"PermissionError: failed to add '{target_path}' to ~/.bashrc", exc_info=True)
		print(Fore.YELLOW + f"Run the installation script as sudo to add '{target_path}' to ~/.bashrc")
	except Exception:
		logger.critical("UnexpectedError:", exc_info=True)
		exit(6)
# unsupported systems
else:
	logger.warning(f"failed to add webserver.py to startup directory / script; your '{sys.platform}' system is not supported")
	print(Fore.YELLOW + f"failed to add webserver.py to startup directory / script; your '{sys.platform}' system is not supported")

# collect metadata
try:
	subprocess.check_call([sys.executable, "collect_metadata.py"])
except Exception:
	logger.error("UnexpectedError:", exc_info=True)
	exit(4)

# start webserver
logger.debug("run webserver.py")
print("Run webserver.py")
try:
	subprocess.check_call([sys.executable, "webserver.py"])
except Exception:
	logger.error("UnexpectedError:", exc_info=True)
	exit(5)

logger.debug(f"end of script: {__file__}")
