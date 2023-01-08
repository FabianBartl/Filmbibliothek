
import json, re, os
from urllib.parse import unquote_plus, quote_plus

from flask import Flask
from flask import redirect, url_for, render_template, send_from_directory

# init flask app and add custom jinja filters 
app = Flask(__name__)
app.jinja_env.filters["urlEncode"] = lambda value: quote_plus(value)

# load movies data file into global variable
with open(os.path.join("static", "movies.json"), "r", encoding="utf-8") as file:
	movies_json = json.load(file)

# set environment variables for useage in templates
@app.context_processor
def utility_processor():
	return {
		"palette": "2-2"
	}

# ---------- url routes ----------

# movie overview
@app.route("/")
def index():
	return render_template("index.html", movies=movies_json)

# see detailed movie data
@app.route('/movie-<movieID>/<moviename>/')
def movie(movieID, moviename):
	return render_template("movie.html", movie=movies_json[movieID])

# watch movie
@app.route('/movie-<movieID>/<moviename>/stream/')
def movie_stream(movieID, moviename):
	return movie_stream_filetype(movieID, moviename, "mp4")

@app.route('/movie-<movieID>/<moviename>/stream/<filetype>/')
def movie_stream_filetype(movieID, moviename, filetype):
	movie_data = movies_json[movieID]
	return send_from_directory(movie_data["directory"], f'{movie_data["filename"]}.{filetype}', as_attachment=False)

# get subtitles
@app.route('/movie-<movieID>/<moviename>/subtitles/<language>/')
def movie_stream_filetype(movieID, moviename, language):
	movie_data = movies_json[movieID]
	return send_from_directory(movie_data["directory"], f'{movie_data["filename"]}.{language}.vtt', as_attachment=False)

# run webserver
if __name__ == "__main__":
	app.run(debug=True)
