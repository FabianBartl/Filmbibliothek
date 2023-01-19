
import os, sys, subprocess

# install python packages
with open("requirements.txt", "r", encoding="utf-8") as file:
    requirements = [ line.strip() for line in file.readlines() ]
for package in requirements:
    if not package in sys.modules:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# these packages are first available after the requirements.txt installation
import winshell, collect_metadata, yaml
from win32com.client import Dispatch
from colorama import Fore, Back, Style, init

init(autoreset=True)
print(Fore.GREEN + "Packages installed")

# load config.yml
with open("config.yml", "r", encoding="utf-8") as file:
    config_yaml = yaml.safe_load(file)

# add host
host = config_yaml.get("server-host", "filmbibliothek")
customHost = False
try:
    with open("C:\\Windows\\System32\\drivers\\etc\\hosts", "r", encoding="utf-8") as file:
        content = file.read()
    with open("C:\\Windows\\System32\\drivers\\etc\\hosts", "a", encoding="utf-8") as file:
        if not host in content:
            file.write(f"\n# host for flask webserver of '{host}' project")
            file.write(f"\n127.0.0.1    {host}\n")
    
    customHost = True
    print(Fore.GREEN + f"Host '{host}' added to DNS resolver")
except PermissionError:
    print(Fore.YELLOW + f"Run the installation script as administrator to add '{host}' as host to local DNS resolver")

# add webserver shortcut to startup
shell = Dispatch("WScript.shell")
shortcut = shell.CreateShortCut(os.path.join(winshell.startup(), f"webserver_{host}.lnk"))
shortcut.Targetpath = os.path.abspath(os.path.join(os.path.curdir, "webserver.py"))
shortcut.WorkingDirectory = os.path.abspath(os.path.curdir)
shortcut.save()
print(Fore.GREEN + "Webserver script added to windows startup directory")

# create movies.json and load movie directory from config.yml
movie_directories = config_yaml.get("movie-directories", [])
if movie_directories == [] or movie_directories == "" or movie_directories == None:
    print(Fore.RED + f"No directories configured")
    print(Fore.YELLOW + "Please add your movie directories to the config.yml file. Then run the installation script again.")
    input(Style.DIM + "Press Enter to close ...")
    exit()
    
if not type(movie_directories) is list:
    movie_directories = [ movie_directories ]

for movie_directory in movie_directories:
    if not os.path.isdir(str(movie_directory)):
        print(Fore.RED + f"Directory '{movie_directory}' not found")
        print(Fore.YELLOW + "Please use valid absolute paths as movie directory. Then run the installation script again.")
        input(Style.DIM + "Press Enter to close ...")
        exit()

# collect metadata
collect_metadata.run(movie_directories)
print(Fore.GREEN + "Movie data collected and stored")

# start webserver
port = config_yaml.get("server-port", 80)
print(
    Fore.GREEN + "The webpage will be available at:",
    Fore.GREEN + f"http://localhost{':'+port if port!=80 else ''}/",
    Fore.GREEN + "or " + Fore.GREEN+f"http://{host}{':'+port if port!=80 else ''}/" if customHost else ""
)

print("Run webserver.py")
subprocess.check_call([sys.executable, "webserver.py"])
