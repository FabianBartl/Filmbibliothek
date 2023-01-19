
import json, yaml, os
from urllib.parse import unquote_plus, quote_plus, unquote, quote
from colorama import Fore, Back, Style, init
init(autoreset=True)

from flask import Flask
from flask import redirect, url_for, render_template, send_from_directory, abort, send_file, request

# ---------- global used variables ----------

MOVIES = {}
CONFIG = {}
DEBUG = False

# init flask app
app = Flask(__name__)

# ---------- functions ----------

# load movies data file into global variable
def load_movies() -> dict:
	with open(os.path.join("static", "data", "movies.json"), "r", encoding="utf-8") as file:
		return json.load(file)

# load config from yaml file
def load_config() -> dict:
	with open("config.yml", "r", encoding="utf-8") as file:
		return yaml.safe_load(file)

# ---------- custom jinja filters ----------

app.jinja_env.filters["urlEncode"] = lambda url: quote_plus(url)

# truncate string and append ellipsis
def truncate(value, length, ellipsis="..."):
	if len(value+ellipsis) > length:
		return value[:length-len(ellipsis)] + ellipsis
	return value
app.jinja_env.filters["truncate"] = truncate

# ---------- jinja context variable ----------

# set context variables for useage in templates
@app.context_processor
def inject_variables():
	global CONFIG
	return {"config": CONFIG, "app_config": app.config}

# ---------- error pages ----------

@app.errorhandler(404)
def not_found(error):
	return render_template("404.html"), 404

# ---------- url routes ----------

# movie overview
@app.route("/")
@app.route("/", methods=["GET"])
def index():
	global MOVIES, DEBUG
	movies_array = str(list(MOVIES.values()))
	search_query = request.args.get("query")
	return render_template("index.html", movies=MOVIES, movies_array=movies_array, search_query=search_query, debug_mode=DEBUG)

# return ANY local file requested by url path
# (Note: Never pass file paths provided by a user to send_file() function)
@app.route("/localpath/<path:filepath>")
def localpath(filepath):
	if os.path.isfile(filepath):
		return send_file(filepath)
	return abort(404)

# favicon image
@app.route("/favicon.ico")
def favicon():
	global CONFIG
	images_dir = os.path.abspath(os.path.join("static", "images"))
	if os.path.isfile(os.path.join(images_dir, favicon := CONFIG.get("favicon"))):
		return send_from_directory(images_dir, favicon, as_attachment=False)
	abort(404)

# detailed movie data
@app.route("/movie/<movieID>/")
def movie(movieID):
	global MOVIES, DEBUG
	if movie := MOVIES.get(movieID):
		return render_template("movie.html", movie=movie, debug_mode=DEBUG)
	return abort(404)

# stream movie
@app.route("/movie/<movieID>/stream/")
def movie_stream(movieID):
	global MOVIES
	if movie := MOVIES.get(movieID):
		return send_from_directory(movie["directory"], f'{movie["filename"]}.{movie["extension"]}', as_attachment=False)
	return abort(404)

# get subtitles
@app.route("/movie/<movieID>/subtitles/<language>/")
def movie_subtitles_language(movieID, language):
	global MOVIES
	if movie := MOVIES.get(movieID):
		if os.path.isfile(os.path.join(movie["directory"], file := f'{movie["filename"]}.{language}.vtt')):
			return send_from_directory(movie["directory"], file, as_attachment=False)
	return abort(404)


# run webserver
if __name__ == "__main__":
	MOVIES = load_movies()
	CONFIG = load_config()

	DEBUG = CONFIG.get("debug-mode", False)
	port = CONFIG.get("server-port", 80)
	if not (port == 80 or port >= 1025):
		print(Fore.RED + "Invalid server port")
		exit()
	
	print(Fore.RED + "DO NOT CLOSE THIS WINDOW")
	app.run(debug=DEBUG, port=port)
