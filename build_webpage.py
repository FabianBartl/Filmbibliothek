
import requests, json, sys, os, re
import urllib.parse
from bs4 import BeautifulSoup
from tqdm import tqdm

# build html structure from movie metadata
def metadataToHTML(metadata:dict) -> str:
    return ""

# readout metadata json file
def getMetadata(filename:str) -> dict:
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)

# save generated html 
def saveAsHTML(filename:str, html:str) -> None:
    with open(filename, "w", encoding="utf-8") as file:
        file.write(html)

# cli
if __name__ == "__main__":
    movies_json = os.path.abspath( sys.argv[1] if len(sys.argv) >= 2 else "movies.json" )
    
    html = []
    for movie_metadata in tqdm(getMetadata(movies_json), unit="Movie", desc="Progress"):
        html.append(metadataToHTML(movie_metadata))
    
    saveAsHTML("index.html", "\n".join(html))
