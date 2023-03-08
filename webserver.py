
import custom_logger
logger = custom_logger.init(__file__, log_to_console=True)
logger.debug(f"start of script: {__file__}")

import json, yaml, minify_html, re, hashlib, time
from math import floor, ceil
from waitress import serve
from os.path import abspath, isfile
from os.path import join as joinpath
from urllib.parse import unquote_plus, quote_plus, unquote, quote
from colorama import Fore, Back, init
init(autoreset=True)

from flask import Flask, Response
from flask import render_template, send_from_directory, abort, request

# ---------- global used variables ----------

MOVIES = {}
CONFIG = {}
DEBUG = True
SERVE = False

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
	except:
		logger.critical(f"UnexpectedError: Couldn't load movie data from '{filename}'", exc_info=True)
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
	except:
		logger.error(f"UnexpectedError: Couldn't load config data from '{filename}'", exc_info=True)
		print(Fore.RED + f"Couldn't load config data from '{filename}'")
		exit(1)

# save movies data file
def save_movies() -> bool:
	global MOVIES
	filename = abspath(joinpath("static", "data", "movies.json"))
	logger.debug(f"try: open {filename=}")
	try:
		with open(filename, "w+", encoding="utf-8") as file:
			logger.debug("dump json data")
			json.dump(MOVIES, file, indent=2)
		return True
	except:
		logger.error(f"UnexpectedError: Couldn't save movie data as JSON in file '{filename}'", exc_info=True)
		return False

# get user rating from user defined yaml file
def getUserRating(filename:str) -> int:
	logger.debug(f"open {filename=}")
	with open(filename, "r+", encoding="utf-8") as file:
		logger.debug("safe load yaml file")
		rating = yaml.safe_load(file).get("user-rating", 0)
		logger.debug(f"loaded {rating=}")
	return rating

# store user rating in user defined yaml file
def setUserRating(filename:str, rating:int) -> None:
	logger.debug(f"open {filename=}")
	with open(filename, "r+", encoding="utf-8") as file:
		metadata = yaml.safe_load(file)
		logger.debug(f"loaded {metadata=}")
	logger.debug(f"open {filename=}")
	with open(filename, "w+", encoding="utf-8") as file:
		logger.debug("dump yaml data")
		metadata["user-rating"] = rating
		yaml.dump(metadata, file, indent=2)
		logger.debug(f"stored {rating=}")

# ---------- custom jinja filters ----------

app.jinja_env.filters["urlEncode"] = quote_plus
app.jinja_env.filters["urlEncodePlus"] = quote
app.jinja_env.filters["urlDecode"] = unquote_plus
app.jinja_env.filters["urlDecodePlus"] = unquote

app.jinja_env.filters["str"] = str
app.jinja_env.filters["int"] = int
app.jinja_env.filters["float"] = float

app.jinja_env.filters["abs"] = abs
app.jinja_env.filters["floor"] = floor
app.jinja_env.filters["ceil"] = ceil

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
def inject_variables() -> dict:
	global CONFIG
	return {"config": CONFIG, "app_config": app.config, "cookies": request.cookies}

logger.debug(f"added yaml config and app config to jinja context")

# ---------- error pages ----------

# @app.errorhandler(204)
def no_content(error_msg:str) -> tuple:
	logger.info(f"app errorhandler: {error_msg}")
	return render_template("204.html", details=error_msg), 204

@app.errorhandler(401)
def unauthorized(error_msg:str) -> tuple:
	logger.error(f"app errorhandler: {error_msg}")
	return render_template("401.html", details=error_msg), 401

@app.errorhandler(403)
def forbidden(error_msg:str) -> tuple:
	logger.error(f"app errorhandler: {error_msg}")
	return render_template("403.html", details=error_msg), 403

@app.errorhandler(404)
def not_found(error_msg:str) -> tuple:
	logger.error(f"app errorhandler: {error_msg}")
	return render_template("404.html", details=error_msg), 404

@app.errorhandler(502)
def bad_gateway(error_msg:str) -> tuple:
	logger.error(f"app errorhandler: {error_msg}")
	return render_template("502.html", details=error_msg), 502

@app.errorhandler(503)
def service_unavailable(error_msg:str) -> tuple:
	logger.error(f"app errorhandler: {error_msg}")
	return render_template("503.html", details=error_msg), 503

# ---------- other flask decorater functions ----------

@app.after_request
def responde_minify(response:Response) -> Response:
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
# error: 404 if icon not found
@app.route("/favicon.ico")
def favicon() -> Response:
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
# error: 404 [not found] if movie not found
@app.route("/movie/<movieID>/")
def movie(movieID:str) -> Response:
	global MOVIES
	if movie := MOVIES.get(movieID):
		return render_template("movie.html", movie=movie)
	return not_found(f"Movie not found.")

# get movie stream
# error: 404 [not found] if movie not found
@app.route("/movie/<movieID>/stream/")
def movie_stream(movieID:str) -> Response:
	global MOVIES
	if movie := MOVIES.get(movieID):
		if isfile(joinpath(movie["movie_directory"], file := f"{movie['filename']}.{movie['extension']}")):
			return send_from_directory(movie["movie_directory"], file, as_attachment=False)
	return not_found(f"Movie not found.")

# get movie poster
# error: 404 [not found] if movie not found
@app.route("/movie/<movieID>/poster/")
def movie_poster(movieID:str) -> Response:
	global MOVIES
	if movie := MOVIES.get(movieID):
		if poster := movie.get("poster"):
			if isfile(joinpath(movie["metadata_directory"], poster)):
				return send_from_directory(movie["metadata_directory"], poster, as_attachment=False)
		return send_from_directory(abspath(joinpath("static", "images")), "blank-poster.jpg")
	return not_found(f"Movie not found.")

# get movie subtitles
# error: 404 [not found] if movie or subtitle file not found
@app.route("/movie/<movieID>/subtitles/<language>/")
def movie_subtitles(movieID:str, language:str) -> Response:
	global MOVIES
	if movie := MOVIES.get(movieID):
		if subtitles := movie.get("subtitles", {}).get(language):
			if isfile(joinpath(movie["metadata_directory"], subtitles)):
				return send_from_directory(movie["metadata_directory"], subtitles, as_attachment=False)
	return not_found(f"Movie not found.")

# set movie user rating
# error: 204 [no content] if user rating saved successfully
#        503 [service unavailable] if saving the user rating failed
#        502 [bad gateway] if stars value is not between 0 and 5 OR if type of stars not integer
#        404 [not found] if movie not found
@app.route("/movie/<movieID>/user-rating/set/<int:stars>")
def movie_user_rating(movieID:str, stars:int) -> Response:
	global MOVIES
	if movie := MOVIES.get(movieID):
		if 0 <= stars <= 5:
			MOVIES[movieID]["user-rating"] = stars
			setUserRating(joinpath(MOVIES[movieID]["metadata_directory"], f"{MOVIES[movieID]['filename']}.yml"), stars)
			return no_content("User rating successfully saved.") if save_movies() else service_unavailable("Failed to save user rating.")
		return bad_gateway("The user rating value must be between 0 and 5.")
	return not_found(f"Movie not found.")
# just to return better error if type of stars is not integer
@app.route("/movie/<movieID>/user-rating/set/<stars>")
def movie_user_rating_error(movieID:str, stars:str) -> Response:
	return bad_gateway(f"User rating value must be of type integer.")

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
	if SERVE:
		serve(app, port=port, host=host)
	else:
		app.run(debug=DEBUG, port=port, host=host)

logger.debug(f"end of script: {__file__}")
