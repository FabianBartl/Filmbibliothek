
import json, yaml, os
from urllib.parse import unquote_plus, quote_plus

from flask import Flask
from flask import redirect, url_for, render_template, send_from_directory, abort, request

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
	return {"config": CONFIG}

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
	
	app.run(debug=DEBUG, port=port)
