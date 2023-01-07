
from bs4 import BeautifulSoup
import urllib.parse
import requests, json, re, os, sys

# readout metadata file and store it as dictionary
def parseMetadata(filename:str) -> dict:
    metadata = {}

    with open(filename, "r", encoding="utf-8") as file:
        metadata["sender"] = file.readline()
        metadata["thema"] = file.readline()
        file.readline()
        metadata["titel"] = file.readline()
        file.readline()
        metadata["datum"] = file.readline()
        metadata["zeit"] = file.readline()
        metadata["dauer"] = file.readline()
        metadata["größe"] = file.readline()
        file.readline()
        file.readline()

        for param in metadata:
            metadata[param] = metadata[param].strip()[13:]

        metadata["website"] = file.readline().strip()
        file.readline()
        file.readline()
        metadata["url"] = file.readline().strip()
        file.readline()

        beschreibung = []
        while line := file.readline():
            if line.strip() == "": continue
            beschreibung.append(line.strip())
        metadata["beschreibung"] = " ".join(beschreibung)

    return metadata


# get movie poster as url
def getMoviePoster(moviename:str, source:str="amazon") -> str:
    header = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36" ,"referer":"https://www.google.com/"}
    
    movienameURL = urllib.parse.quote_plus(f"filmplakat \"{moviename}\"")
    if source == "amazon":
        requestURL = "https://www.amazon.de/s?k=" + movienameURL
    elif source == "bing":
        requestURL = "https://www.bing.com/images/search?q=" + movienameURL + "&qft=+filterui:aspect-tall&first=1&tsc=ImageHoverTitle&cw=1177&ch=705"
    elif source == "google":
        pass
    elif source == "ebay":
        pass
    else:
        raise ValueError(f"unknow source: {source}")

    input(requestURL)

    request = requests.get(requestURL, headers=header)
    if request.status_code != 200:
        raise Exception(f"HTTP response code: {request.status_code}")
    html = BeautifulSoup(request.content, features="html.parser")
    
    with open("request.html", "wb") as file:
        file.write(request.content)

    if source == "amazon":
        img = html.body.find(attrs={"alt": moviename})
        if img is None:
            raise Exception("Related image not found")
        return img.get("data-src")
    
    elif source == "bing":
        imgs = [ tag for tag in html.body.findAll(attrs={"class": "iusc"}) if tag.get("class") == ["iusc"] ]
        if imgs == []:
            raise Exception("Related image not found")

        imgURL = [ param.replace("mediaurl=", "") for param in imgs[0].get("href").split("&") if param.startswith("mediaurl=") ]
        if imgURL == []:
            raise Exception("Related image not found")
        return urllib.parse.unquote(imgURL[0])

    elif source == "google":
        pass

    elif source == "ebay":
        pass


metadata = parseMetadata(r"C:\Users\fabia\OneDrive\Dokumente\GitHub\video-library\Videos\23 - Nichts ist so wie es scheint.txt")
print(metadata)

moviePoster = getMoviePoster("23 - Nichts ist so wie es scheint", "bing")
print(moviePoster)

