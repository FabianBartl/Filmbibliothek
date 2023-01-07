
import requests, json, sys, os, re
import urllib.parse
from bs4 import BeautifulSoup
from tqdm import tqdm

from flask import Flask, redirect, url_for, render_template
app = Flask(__name__)

@app.route("/")
def index():
    with open("movies.json", "r", encoding="utf-8") as file:
        movies_json = json.load(file)
    return render_template("index.html", movies=movies_json)

if __name__ == "__main__":
    app.run(debug=True)
