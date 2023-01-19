
import os, sys, yaml, subprocess

# install python packages
try:
    import winshell, collect_metadata
    from win32com.client import Dispatch
    from colorama import Fore, Back, Style, init
    
    init(autoreset=True)
    print(Fore.GREEN + "Packages already installed")

except:
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
    print(Fore.YELLOW + f"Run the installation script as administrator to add '{host}' as host to DNS resolver")

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
    print("Please add your movie directories to the config.yml file. Then run the installation script again.")
    input(Style.DIM + "Press Enter to close ...")
    exit()
    
if not type(movie_directories) is list:
    movie_directories = [ movie_directories ]

for movie_directory in movie_directories:
    if not os.path.isdir(str(movie_directory)):
        print(Fore.RED + f"Directory '{movie_directory}' not found")
        print("Please use valid absolute paths as movie directory. Then run the installation script again.")
        input(Style.DIM + "Press Enter to close ...")
        exit()

# collect metadata
collect_metadata.run(movie_directories)

print(Fore.GREEN + "Movie data collected and stored")

# start webserver via system restart
port = config_yaml.get("server-port", 80)
if port == 80:
    print(Fore.YELLOW+"After restarting, the webpage will be available at: http://localhost/", Fore.YELLOW+"or "+Fore.GREEN+f"http://{host}/" if customHost else "")
else:
    print(Fore.YELLOW+f"After restarting, the webpage will be available at: localhost:{port}/", Fore.YELLOW+"or "+Fore.GREEN+f"{host}:{port}/" if customHost else "")
