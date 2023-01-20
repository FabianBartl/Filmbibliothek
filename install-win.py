
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
import winshell, collect_metadata, yaml
from win32com.client import Dispatch
from colorama import Fore, Back, Style, init

init(autoreset=True)
print(Fore.GREEN + "Packages installed")

# load config.yml
logger.debug("load config.yml")
with open("config.yml", "r", encoding="utf-8") as file:
    config_yaml = yaml.safe_load(file)
    logger.info("config.yml loaded")

# add host
logger.debug("try: add host to local dns resolver")
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
    logger.info(f"added {host=} to local dns resolver")
    print(Fore.GREEN + f"Host '{host}' added to DNS resolver")
except PermissionError:
    logger.warning(f"failed to add {host=} to local dns resolver")
    print(Fore.YELLOW + f"Run the installation script as administrator to add '{host}' as host to local DNS resolver")

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

# create movies.json and load movie directories from config.yml
logger.debug(f"load movie directories from config.yml")
movie_directories = config_yaml.get("movie-directories", [])
if movie_directories == [] or movie_directories == "" or movie_directories == None:
    logger.error("no movie directories configured")
    print(Fore.RED + f"No directories configured")
    print(Fore.YELLOW + "Please add your movie directories to the config.yml file. Then run the installation script again.")
    input(Style.DIM + "Press Enter to close ...")
    exit()
    
if not type(movie_directories) is list:
    logger.debug(f"convert single movie directory string to list: {movie_directories=}")
    movie_directories = [ movie_directories ]
    logger.debug(f"as list: {movie_directories=}")

logger.debug("check validity of movie directories")
for movie_directory in movie_directories:
    if not os.path.isdir(str(movie_directory)):
        logger.error(f"directory {movie_directory=} not found")
        print(Fore.RED + f"Directory '{movie_directory}' not found")
        print(Fore.YELLOW + "Please use valid absolute paths as movie directory. Then run the installation script again.")
        input(Style.DIM + "Press Enter to close ...")
        exit()

# collect metadata
logger.debug(f"run collect_metadata.py with {movie_directories=}")
collect_metadata.run(movie_directories)
logger.info("movie data collected and stored")
print(Fore.GREEN + "Movie data collected and stored")

# start webserver
port = config_yaml.get("server-port", 80)
logger.debug(f"show webserver address: {host=} {port=}")
print(
    Fore.GREEN + "The webpage will be available at:",
    Fore.GREEN + f"http://localhost{':'+port if port!=80 else ''}/",
    Fore.GREEN + "or " + Fore.GREEN+f"http://{host}{':'+port if port!=80 else ''}/" if customHost else ""
)

logger.debug("run webserver.py")
print("Run webserver.py")
subprocess.check_call([sys.executable, "webserver.py"])

logger.debug(f"end of script: {__file__}")
