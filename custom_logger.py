
import logging, os
from datetime import datetime


# https://alexandra-zaharia.github.io/posts/make-your-own-custom-color-formatter-with-python-logging/
# https://stackoverflow.com/a/56944256/3638629
class CustomFormatter(logging.Formatter):
	def __init__(self, *, fmt:str, datefmt:str, colored:bool):
		# init inherited class
		super().__init__()
		self.fmt = fmt
		self.datefmt = datefmt
		self.colored = colored
		
		# use colored output if configured and colorama is installed
		try:
			if not self.colored:
				raise Exception(f"{self.colored=}")
			# try import and init colorama
			from colorama import Fore, Back, Style, init
			init(autoreset=True)
			# set colored formats
			reset_color = Fore.RESET + Back.RESET + Style.RESET_ALL
			self.FORMATS = {
				logging.DEBUG: Style.DIM + self.fmt + reset_color,
				logging.INFO: Fore.BLUE + self.fmt + reset_color,
				logging.WARNING: Fore.YELLOW + self.fmt + reset_color,
				logging.ERROR: Fore.RED + Style.BRIGHT + self.fmt + reset_color,
				logging.CRITICAL: Fore.WHITE + Back.RED + self.fmt + reset_color,
			}
		# use not colored output
		except:
			self.FORMATS = {
				logging.DEBUG: self.fmt, 
				logging.INFO: self.fmt,
				logging.WARNING: self.fmt,
				logging.ERROR: self.fmt,
				logging.CRITICAL: self.fmt
			}

	def format(self, record):
		format = self.FORMATS.get(record.levelno, self.fmt)
		formatter = logging.Formatter(fmt=format, datefmt=self.datefmt)
		return formatter.format(record)


# returns configured logging handler object
def init(name, *, name_is_path:bool=True, log_to_file:bool=True, log_to_console:bool=False, log_level:int=logging.DEBUG, colored_console:bool=True):
	# extract filename from path
	if name_is_path:
		name = os.path.basename(name)

	# logging parameter
	level = log_level
	timestamp = datetime.today().strftime("%Y-%m-%d_%H-%M-%S")
	path = os.path.abspath(os.path.join("logs", f"{name}_{timestamp}.log"))
	encoding = "utf-8"
	format = "%(asctime)s | %(levelname)8s | %(message)s"
	datefmt = "%Y-%m-%d %H:%M:%S"

	# logging handlers
	handlers = []

	# file handler
	if log_to_file:
		file_handler = logging.FileHandler(path, encoding=encoding)
		file_handler.setLevel(level)
		file_handler.setFormatter(logging.Formatter(fmt=format, datefmt=datefmt))
		handlers.append(file_handler)

	# console handler
	if log_to_console:
		console_handler = logging.StreamHandler()
		console_handler.setLevel(level)
		console_handler.setFormatter(CustomFormatter(fmt=format, datefmt=datefmt, colored=colored_console))
		handlers.append(console_handler)

	# logging config
	logging.basicConfig(level=level, encoding=encoding, format=format, datefmt=datefmt, handlers=handlers)

	return logging.getLogger(name)


# converts logging level string to corresponding level integer
def level_to_int(level:str) -> int:
	levels = {
		"DEBUG": logging.DEBUG,
		"INFO": logging.INFO,
		"WARNING": logging.WARNING,
		"ERROR": logging.ERROR,
		"CRITICAL": logging.CRITICAL,
	}
	return levels.get(level, logging.DEBUG)
