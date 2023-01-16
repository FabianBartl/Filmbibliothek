
import os, sys, yaml, subprocess

# install python packages
with open("requirements.txt", "r", encoding="utf-8") as file:
	requirements = [ line.strip() for line in file.readlines() ]
for package in requirements:
	if not package in sys.modules:
		subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# these packages are first available after the requirements.txt installation
import winshell, collect_metadata
from win32com.client import Dispatch
from colorama import Fore, Back, Style, init
init(autoreset=True)

print(Fore.GREEN + "Packages installed\n")

# add host
host = "filmbibliothek"
with open("C:\\Windows\\System32\\drivers\\etc\\hosts", "r", encoding="utf-8") as file:
    content = file.read()
with open("C:\\Windows\\System32\\drivers\\etc\\hosts", "a", encoding="utf-8") as file:
    if not host in content:
        file.write(f"\n# host for flask webserver of '{host}' project")
        file.write(f"\n127.0.0.1    {host}\n")

print(Fore.GREEN + f"Host '{host}' added to DNS resolver\n")

# create movies.json and store movie_directory in config.yml
while not os.path.isdir(movie_directory := input("Movie directory: ")):
    print(Fore.RED + "Directory not found\n")
# load config.yml
with open("config.yml", "r", encoding="utf-8") as file:
    config_yaml = yaml.safe_load(file)
    config_yaml["movie_directories"] = [os.path.abspath(movie_directory)]
# store movie_directory in config.yml
with open("config.yml", "w+", encoding="utf-8") as file:
    yaml.dump(config_yaml, file)
# collect metadata
collect_metadata.run(config_yaml["movie_directories"])

print(Fore.GREEN + "Movie data collected and stored\n")

# add webserver shortcut to startup
shell = Dispatch("WScript.shell")
shortcut = shell.CreateShortCut(os.path.join(winshell.startup(), f"webserver_{host}.lnk"))
shortcut.Targetpath = os.path.abspath(os.path.join(os.path.curdir, "webserver.py"))
shortcut.WorkingDirectory = os.path.abspath(os.path.curdir)
shortcut.save()

print(Fore.GREEN + "Webserver added to windows startup directory\n")

# start webserver via system restart
print(Fore.YELLOW + "Please restart your system\n")

# TODO: add client shortcut to desktop
print(Fore.YELLOW + f"After restarting, the webpage will be available at: http://localhost/ or http://{host}/\n")
