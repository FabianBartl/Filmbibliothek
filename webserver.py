
import custom_logger
logger = custom_logger.init(__file__, log_to_console=True)
logger.debug(f"start of script: {__file__}")

import json, yaml, os
from urllib.parse import unquote_plus, quote_plus, unquote, quote
from colorama import Fore, Back, Style, init
init(autoreset=True)

from flask import Flask
from flask import redirect, url_for, render_template, send_from_directory, abort, send_file, request, jsonify

# ---------- global used variables ----------

MOVIES = {}
CONFIG = {}

# init flask app
app = Flask(__name__)

logger.debug(f"global variables initialized")

# ---------- functions ----------

# load movies data file into global variable
def load_movies() -> dict:
	filename = os.path.abspath(os.path.join("static", "data", "movies.json"))
	logger.debug(f"try: open {filename=}")
	try:
		with open(filename, "r", encoding="utf-8") as file:
			data = json.load(file)
			logger.info("loaded json movie data")
			return data
	# unexpected error
	except Exception as error:
		logger.critical(error)
		print(Fore.RED + f"Couldn't load movie data from '{filename}'")
		exit(1)

# load config from yaml file
def load_config() -> dict:
	filename = os.path.abspath("config.yml")
	logger.debug(f"try: open {filename=}")
	try:
		with open(filename, "r", encoding="utf-8") as file:
			data = yaml.safe_load(file)
			logger.info("loaded yaml config data")
			return data
	# unexpected error
	except Exception as error:
		logger.critical(error)
		print(Fore.RED + f"Couldn't load config data from '{filename}'")
		exit(1)

# ---------- custom jinja filters ----------

app.jinja_env.filters["urlEncode"] = lambda url: quote_plus(url)
app.jinja_env.filters["urlEncodePlus"] = lambda url: quote(url)

# truncate string and append ellipsis
def truncate(value, length, ellipsis="..."):
	if len(value+ellipsis) > length:
		return value[:length-len(ellipsis)] + ellipsis
	return value
app.jinja_env.filters["truncate"] = truncate

logger.debug(f"custom jinja filters defined")

# ---------- jinja context variable ----------

# set context variables for useage in templates
@app.context_processor
def inject_variables():
	global CONFIG
	return {"config": CONFIG, "app_config": app.config}

logger.debug(f"added yaml config and app config to jinja context")

# ---------- error pages ----------

@app.errorhandler(404)
def not_found(error):
	return render_template("404.html"), 404

# ---------- url routes ----------

# get favicon
@app.route("/favicon.ico")
def favicon():
	global CONFIG
	images_dir = os.path.abspath(os.path.join("static", "images"))
	if os.path.isfile(os.path.join(images_dir, favicon := CONFIG.get("favicon"))):
		return send_from_directory(images_dir, favicon, as_attachment=False)
	abort(404)

# return movie overview page
@app.route("/")
@app.route("/", methods=["GET"])
def index():
	global MOVIES
	movies_array = str(list(MOVIES.values()))
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
			if os.path.isfile(os.path.join(movie["metadata_directory"], poster)):
				return send_from_directory(movie["metadata_directory"], poster, as_attachment=False)
		return send_from_directory(os.path.abspath(os.path.join("static", "images")), "blank-poster.jpg")
	return abort(404)

# get movie subtitles
@app.route("/movie/<movieID>/subtitles/<language>/")
def movie_subtitles(movieID, language):
	global MOVIES
	if movie := MOVIES.get(movieID):
		if subtitles := movie.get("subtitles", {}).get(language):
			if os.path.isfile(os.path.join(movie["metadata_directory"], subtitles)):
				return send_from_directory(movie["metadata_directory"], subtitles, as_attachment=False)
	return abort(404)

# ---------- temporary test functions ----------

@app.route("/get_my_ip")
def get_my_ip():
	return str(request.headers.get("X-Forwarded-For")), 200

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
	app.run(debug=True, port=port, host=host)

logger.debug(f"end of script: {__file__}")
