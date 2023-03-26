
import logging
from datetime import datetime

from os.path import abspath, basename
from os.path import join as joinpath

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


# return a logging handler for a colored tqdm progress bar
# def getTqdmHandler( tqdm_progressBar: tqdm, level: int ) -> TqdmLoggingHandler
def getTqdmHandler(tqdm_progressBar, level:int, colored:bool=True):
	try:
		import tqdm

		class TqdmLoggingHandler(logging.Handler):
			def __init__(self, progress_bar:tqdm, level:int):
				super().__init__(level)
				self.progress_bar = progress_bar
				self.counter = {
					logging.DEBUG: 0,
					logging.INFO: 0,
					logging.WARNING: 0,
					logging.ERROR: 0,
					logging.CRITICAL: 0
				}

			def emit(self, record):
				if record.levelno in self.counter:
					# count logs
					self.counter[record.levelno] += 1
					# skip most debug and info colorings to show more important colors longer
					if (self.counter[record.levelno] % 20 != 0 and logging.DEBUG == record.levelno) or \
						(self.counter[record.levelno] % 5 != 0 and logging.INFO == record.levelno):
						return
				# set color and refresh bar
				if colored:
					self.progress_bar.colour = level_to_color(record.levelno)
				self.progress_bar.refresh()
		
		return TqdmLoggingHandler(tqdm_progressBar, level)
	
	except Exception as error:
		logging.error("failed to create handler for colored tqdm progress bar")
		logging.error(error)
		return None


# returns configured logging handler object
def init(name, *, name_is_path:bool=True, log_to_file:bool=True, log_to_console:bool=False, log_level:int=logging.DEBUG, colored_console:bool=True) -> logging.Logger:
	# extract filename from path
	if name_is_path:
		name = basename(name)

	# logging parameter
	level = log_level
	timestamp = datetime.today().strftime("%d-%m-%Y_%H-%M-%S")
	path = abspath(joinpath("logs", f"{name}_{timestamp}.log"))
	encoding = "utf-8"
	format = "[ %(levelname)8s ]  [ %(asctime)s ]  %(message)s"
	datefmt = "%d/%m/%Y %H:%M:%S"

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

# converts logging level integer to corresponding hex color of level
def level_to_color(level:int, default:str=None) -> str:
	levels = {
		logging.DEBUG: "#7F7D7A",
		logging.INFO: "#008DF8",
		logging.WARNING: "#FFB900",
		logging.ERROR: "#FF2740",
		logging.CRITICAL: "#008DF8"
	}
	return levels.get(level, default)
