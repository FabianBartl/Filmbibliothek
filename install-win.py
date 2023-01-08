
import os

# install python packages
os.system("pip install -r requirements.txt")

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

# create movies.json
while not os.path.isdir(movie_directory := input("Movie directory: ")):
    print(Fore.RED + "Directory not found\n")
collect_metadata.run(os.path.abspath(movie_directory))

print(Fore.GREEN + "Movie data collected and stored\n")

# add webserver to startup
shell = Dispatch("WScript.shell")
shortcut = shell.CreateShortCut(os.path.join(winshell.startup(), f"webserver_{host}.lnk"))
shortcut.Targetpath = os.path.abspath(os.path.join(os.path.curdir, "webserver.py"))
shortcut.WorkingDirectory = os.path.abspath(os.path.curdir)
shortcut.save()

print(Fore.GREEN + "Webserver added to windows startup directory\n")
