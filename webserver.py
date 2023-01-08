
import json
import urllib.parse

from jinja2 import Environment
from flask import Flask
from flask import redirect, url_for, render_template, send_from_directory

app = Flask(__name__)
# app.jinja_env = Environment()

# app.jinja_env.filters["urlEncode"] = lambda value: urllib.parse.quote_plus(value)

@app.route("/")
def index():
    with open("movies.json", "r", encoding="utf-8") as file:
        movies_json = json.load(file)
    return render_template("index.html", movies=movies_json)

@app.route('/movie/<moviename>/stream/')
def movie_show(moviename):
    movie_library = "C:\\Users\\fabia\\OneDrive\\Dokumente\\Originals\\Filme"
    return send_from_directory(movie_library, f"{urllib.parse.unquote(moviename)}.mp4", as_attachment=False )


if __name__ == "__main__":
    app.run(debug=True)
