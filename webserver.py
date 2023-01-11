
import json, os
from urllib.parse import unquote_plus, quote_plus

from flask import Flask
from flask import redirect, url_for, render_template, send_from_directory

# init flask app
app = Flask(__name__)

# load movies data file into global variable
def load_movies() -> dict:
	with open(os.path.join("static", "data", "movies.json"), "r", encoding="utf-8") as file:
		return json.load(file)
movies_json = load_movies()

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
	return {"palette": "2-2"}

# ---------- url routes ----------

# movie overview
@app.route("/")
def index():
	return render_template("index.html", movies=movies_json)

# detailed movie data
@app.route("/movie/<movieID>/")
def movie(movieID):
	return render_template("movie.html", movie=movies_json[movieID])

# stream movie
@app.route("/movie/<movieID>/stream/")
def movie_stream(movieID):
	movie_data = movies_json[movieID]
	return send_from_directory(movie_data["directory"], f'{movie_data["filename"]}.{movie_data["extension"]}', as_attachment=False)

# get subtitles
@app.route("/movie/<movieID>/subtitles/<language>/")
def movie_subtitles_language(movieID, language):
	movie_data = movies_json[movieID]
	return send_from_directory(movie_data["directory"], f'{movie_data["filename"]}.{language}.vtt', as_attachment=False)

# search for software updates
@app.route("/update/")
def update_software():
	return render_template("update_software.html")

# re-load movie data
@app.route("/reload/")
def reload_moviedata():
	return render_template("reload_moviedata.html")


# run webserver
if __name__ == "__main__":
	app.run(debug=True, port=80)
