
import json, os
from urllib.parse import unquote_plus, quote_plus

from flask import Flask
from flask import redirect, url_for, render_template, send_from_directory, abort, request

# ---------- functions ----------

# load movies data file into global variable
def load_movies() -> dict:
	with open(os.path.join("static", "data", "movies.json"), "r", encoding="utf-8") as file:
		return json.load(file)
movies_json = load_movies()

# search for software updates
def update_software():
	pass

# reload movie data stored in movies_json
def reload_movies():
	global movies_json
	movies_json = load_movies()

# collect metadata and reload movie data
def collect_metadata():
	pass

# init flask app
app = Flask(__name__)

# ---------- custom jinja filters ----------

app.jinja_env.filters["urlEncode"] = lambda value: quote_plus(value)

# truncate string and append ellipsis
def truncate(value, length, ellipsis="..."):
	if len(value+ellipsis) > length:
		return value[:length-len(ellipsis)] + ellipsis
	return value
app.jinja_env.filters["truncate"] = truncate

# ---------- jinja context variable ----------

# set context variables for useage in templates
@app.context_processor
def utility_processor():
	return {"config": {"theme": "dark"}}

# ---------- error pages ----------

@app.errorhandler(404)
def not_found(error):
	return render_template("404.html"), 404

# ---------- url routes ----------

# movie overview
@app.route("/")
@app.route("/", methods=["POST"])
def index():
	global movies_json
	# post actions
	if request.form.get("update_software"): update_software()
	if request.form.get("reload_movies"): reload_movies()
	if request.form.get("collect_metadata"): collect_metadata()
	return render_template("index.html", movies=movies_json)

# detailed movie data
@app.route("/movie/<movieID>/")
def movie(movieID):
	global movies_json
	if movie := movies_json.get(movieID):
		return render_template("movie.html", movie=movie)
	return abort(404)

# stream movie
@app.route("/movie/<movieID>/stream/")
def movie_stream(movieID):
	global movies_json
	if movie_data := movies_json.get(movieID):
		return send_from_directory(movie_data["directory"], f'{movie_data["filename"]}.{movie_data["extension"]}', as_attachment=False)
	return abort(404)

# get subtitles
@app.route("/movie/<movieID>/subtitles/<language>/")
def movie_subtitles_language(movieID, language):
	global movies_json
	if movie_data := movies_json.get(movieID):
		if os.path.isfile(os.path.join(movie_data["directory"], file := f'{movie_data["filename"]}.{language}.vtt')):
			return send_from_directory(movie_data["directory"], file, as_attachment=False)
	return abort(404)

# run webserver
if __name__ == "__main__":
	app.run(debug=True, port=80)
