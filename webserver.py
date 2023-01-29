
import custom_logger
logger = custom_logger.init(__file__, log_to_console=True)
logger.debug(f"start of script: {__file__}")

import json, yaml, minify_html, re, hashlib, time
from os.path import abspath, isfile
from os.path import join as joinpath
from urllib.parse import unquote_plus, quote_plus, unquote, quote
from colorama import Fore, Back, init
init(autoreset=True)

from flask import Flask
from flask import render_template, send_from_directory, abort, request

# ---------- global used variables ----------

MOVIES = {}
CONFIG = {}
DEBUG = False

# init flask app
app = Flask(__name__)

logger.debug(f"global variables initialized")

# ---------- functions ----------

# load movies data file into global variable
def load_movies() -> dict:
	filename = abspath(joinpath("static", "data", "movies.json"))
	logger.debug(f"try: open {filename=}")
	try:
		with open(filename, "r", encoding="utf-8") as file:
			data = json.load(file)
			logger.debug("loaded json movie data")
			return data
	# unexpected error
	except Exception as error:
		logger.error(f"Couldn't load movie data from '{filename}'")
		logger.critical(error)
		print(Fore.RED + f"Couldn't load movie data from '{filename}'")
		exit(1)

# load config from yaml file
def load_config() -> dict:
	filename = abspath("config.yml")
	logger.debug(f"try: open {filename=}")
	try:
		with open(filename, "r", encoding="utf-8") as file:
			data = yaml.safe_load(file)
			logger.debug("loaded yaml config data")
			return data
	# unexpected error
	except Exception as error:
		logger.error(f"Couldn't load config data from '{filename}'")
		logger.critical(error)
		print(Fore.RED + f"Couldn't load config data from '{filename}'")
		exit(1)

# ---------- custom jinja filters ----------

app.jinja_env.filters["urlEncode"] = lambda this: quote_plus(this)
app.jinja_env.filters["urlEncodePlus"] = lambda this: quote(this)
app.jinja_env.filters["urlDecode"] = lambda this: unquote_plus(this)
app.jinja_env.filters["urlDecodePlus"] = lambda this: unquote(this)

app.jinja_env.filters["str"] = str
app.jinja_env.filters["int"] = int
app.jinja_env.filters["abs"] = abs
app.jinja_env.filters["float"] = float

app.jinja_env.filters["md5"] = lambda this: hashlib.md5(this.encode("utf-8")).hexdigest()

# truncate string and append ellipsis
def truncate(this:str, length:int, ellipsis:str="...") -> str:
	if len(this+ellipsis) > length:
		return this[:length-len(ellipsis)] + ellipsis
	return this
app.jinja_env.filters["truncate"] = truncate

# return the time difference between 'this' timestamp and now or given timestamp
def time_difference(this:int, timestamp:int=None) -> int:
	if timestamp is None:
		return this - time.time()
	else:
		return this - timestamp
app.jinja_env.filters["time_difference"] = time_difference

# find first integer in string
def first_integer(this:str, default:int) -> int:
	matches = re.findall(r"\d+", this)
	if len(matches) == 0:
		return default
	return int(matches[0])
app.jinja_env.filters["first_integer"] = first_integer

logger.debug(f"custom jinja filters defined")

# ---------- jinja context variable ----------

# set context variables for useage in templates
@app.context_processor
def inject_variables():
	global CONFIG
	return {"config": CONFIG, "app_config": app.config, "cookies": request.cookies}

logger.debug(f"added yaml config and app config to jinja context")

# ---------- error pages ----------

@app.errorhandler(404)
def not_found(error):
	return render_template("404.html"), 404

# ---------- other flask decorater functions ----------

@app.before_first_request
def get_client_ip():
	if client_ip := request.headers.get("x-forwarded-for"):
		logger.warning(f"{client_ip=}")

@app.after_request
def responde_minify(response):
	global DEBUG
	# minfy html, except in debug mode
	if response.content_type == u"text/html; charset=utf-8" and not DEBUG:
		response.set_data(minify_html.minify(
			response.get_data(as_text=True),
			minify_js = True,
			do_not_minify_doctype = True,
			keep_spaces_between_attributes = True,
			ensure_spec_compliant_unquoted_attribute_values = True
		))
	return response

# ---------- url routes ----------

# get favicon
@app.route("/favicon.ico")
def favicon():
	global CONFIG
	images_dir = abspath(joinpath("static", "images"))
	if isfile(joinpath(images_dir, favicon := CONFIG.get("favicon"))):
		return send_from_directory(images_dir, favicon, as_attachment=False)
	abort(404)

# return movie overview page
@app.route("/")
@app.route("/", methods=["GET"])
def index():
	global MOVIES
	# convert nested objects to repr strings
	movies_array = json.dumps([ dict({ key: str(value) for key, value in obj.items() }) for obj in MOVIES.values() ])
	search_query = request.args.get("query")
	return render_template("index.html", movies=MOVIES, movies_array=movies_array, search_query=search_query)

# return detailed movie page
@app.route("/movie/<movieID>/")
def movie(movieID):
	global MOVIES
	if movie := MOVIES.get(movieID):
		return render_template("movie.html", movie=movie)
	return abort(404)

# get movie stream
@app.route("/movie/<movieID>/stream/")
def movie_stream(movieID):
	global MOVIES
	if movie := MOVIES.get(movieID):
		return send_from_directory(movie["movie_directory"], f"{movie['filename']}.{movie['extension']}", as_attachment=False)
	return abort(404)

# get movie poster
@app.route("/movie/<movieID>/poster/")
def movie_poster(movieID):
	global MOVIES
	if movie := MOVIES.get(movieID):
		if poster := movie.get("poster"):
			if isfile(joinpath(movie["metadata_directory"], poster)):
				return send_from_directory(movie["metadata_directory"], poster, as_attachment=False)
		return send_from_directory(abspath(joinpath("static", "images")), "blank-poster.jpg")
	return abort(404)

# get movie subtitles
@app.route("/movie/<movieID>/subtitles/<language>/")
def movie_subtitles(movieID, language):
	global MOVIES
	if movie := MOVIES.get(movieID):
		if subtitles := movie.get("subtitles", {}).get(language):
			if isfile(joinpath(movie["metadata_directory"], subtitles)):
				return send_from_directory(movie["metadata_directory"], subtitles, as_attachment=False)
	return abort(404)

# ---------- start routine ----------

# load movies and config
MOVIES = load_movies()
logger.debug(f"movies loaded")
CONFIG = load_config()
logger.debug(f"config loaded: {CONFIG=}")

# update logging level
log_level = custom_logger.level_to_int(CONFIG.get("log-level"))
logger.setLevel(log_level)
logger.info(f"update logger lever to {log_level}")

# load port, name and host
name = CONFIG.get("server-name", "filmbibliothek")
app.name = name
host = "0.0.0.0" if CONFIG.get("accessible-in-network") else "127.0.0.1"
port = CONFIG.get("server-port", 80)
if not (port == 80 or port >= 1025):
	logger.critical(f"invalid server port {port}")
	print(Fore.RED + f"Invalid server port: {port}")
	exit(2)

# run flask app
if __name__ == "__main__":
	print(Fore.WHITE + Back.RED + "    DO NOT CLOSE THIS WINDOW    ")
	logger.info(f"run flask app as {name=} and {port=} on {host=}")
	print(Fore.GREEN + f"open in webbrowser as http://{name}:{port}/ or http://localhost:{port}/")
	if host == "0.0.0.0":
		logger.info("accessible in network")
		print(Fore.YELLOW + f"accessible in your local network using the local network address of your host-computer")
	# run app
	app.run(debug=DEBUG, port=port, host=host)

logger.debug(f"end of script: {__file__}")
