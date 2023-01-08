
import json, requests, sys, os, re
import urllib.parse

from flask import Flask
from flask import redirect, url_for, render_template, send_from_directory

app = Flask(__name__)

@app.route("/")
def index():
    with open("movies.json", "r", encoding="utf-8") as file:
        movies_json = json.load(file)
    return render_template("index.html", movies=movies_json)

@app.route('/movie/<moviename>')
def movie_show(moviename):
    return send_from_directory("Videos", moviename, as_attachment=True, )

if __name__ == "__main__":
    app.run(debug=True)
