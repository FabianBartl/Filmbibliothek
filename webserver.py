
import json, re, os
from urllib.parse import unquote_plus, quote_plus

from flask import Flask
from flask import redirect, url_for, render_template, send_from_directory

# init flask app and add custom jinja filters 
app = Flask(__name__)
app.jinja_env.filters["urlEncode"] = lambda value: quote_plus(value)

# load movies data file into global var
with open(os.path.join("static", "movies.json"), "r", encoding="utf-8") as file:
    movies_json = json.load(file)

# returns movie data from movies json 
def getMovieData(moviename:str) -> dict:
    for _, data in movies_json.items():
        if re.sub(r"[^\W]*", "", data["title"]).lower() == re.sub(r"[^\W]*", "", moviename).lower():
            return data
    return {}

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
    movie_data = movies_json[movieID]
    return send_from_directory(movie_data["directory"], movie_data["filename"], as_attachment=False)

# run webserver
if __name__ == "__main__":
    app.run(debug=True)
