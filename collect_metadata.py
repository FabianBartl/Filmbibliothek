
import requests, json
import urllib.parse
from bs4 import BeautifulSoup
from tqdm import tqdm

# readout metadata file and store it as dictionary
def parseMetadata(filename:str) -> dict:
    metadata = {}

    with open(filename, "r", encoding="utf-8") as file:
        metadata["channel"] = file.readline()
        metadata["topc"] = file.readline()
        file.readline()
        metadata["title"] = file.readline()
        file.readline()
        metadata["date"] = file.readline()
        metadata["time"] = file.readline()
        metadata["duration"] = file.readline()
        metadata["filesize"] = file.readline()
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
        metadata["description"] = " ".join(beschreibung)

    return metadata


# get movie poster as url
def getMoviePoster(moviename:str, source:str="imdb") -> str:
    relImgNotFound = Exception("Related image not found")
    header = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36" ,"referer":"https://www.google.com/"}
    
    movienameURL = urllib.parse.quote_plus(moviename)
    if source == "amazon":
        requestURL = "https://www.amazon.de/s?k=" + movienameURL
    elif source == "bing":
        requestURL = "https://www.bing.com/images/search?q=" + movienameURL + "&qft=+filterui:aspect-tall&first=1&tsc=ImageHoverTitle&cw=1177&ch=705"
    elif source == "google":
        pass
    elif source == "ebay":
        pass
    elif source == "imdb":
        requestURL = "https://www.imdb.com/find/?q=" + movienameURL
    else:
        raise ValueError(f"unknow source: {source}")

    request = requests.get(requestURL, headers=header)
    if request.status_code != 200:
        raise Exception(f"HTTP response code: {request.status_code}")
    html = BeautifulSoup(request.content, features="html.parser")
    
    with open("request.html", "wb") as file:
        file.write(request.content)

    if source == "amazon":
        img = html.body.find("img", attrs={"alt": moviename})
        if img is None:
            raise relImgNotFound
        return img.get("data-src")
    
    elif source == "bing":
        imgs = [ tag for tag in html.body.findAll(attrs={"class": "iusc"}) if tag.get("class") == ["iusc"] ]
        if imgs == []:
            raise relImgNotFound

        imgURL = [ param.replace("mediaurl=", "") for param in imgs[0].get("href").split("&") if param.startswith("mediaurl=") ]
        if imgURL == []:
            raise relImgNotFound
        return urllib.parse.unquote(imgURL[0])

    elif source == "google":
        pass

    elif source == "ebay":
        pass

    elif source == "imdb":
        page = html.body.find("a", attrs={"class": "ipc-metadata-list-summary-item__t"})
        if page is None:
            raise relImgNotFound
        pageURL = "https://www.imdb.com" + page.get("href")

        request = requests.get(pageURL, headers=header)
        if request.status_code != 200:
            raise Exception(f"HTTP response code: {request.status_code}")
        html = BeautifulSoup(request.content, features="html.parser")

        with open("request_page.html", "wb") as file:
            file.write(request.content)
        
        imgs = [ tag for tag in html.body.findAll("img", attrs={"class": "ipc-image"}) if tag.get("class") == ["ipc-image"] ]
        if imgs == []:
            raise relImgNotFound
        return imgs[0].get("srcset").split(", ")[-1].split(" ")[0]


# save collected metadata as json format
def saveMetadata(filename:str, metadata:dict) -> None:
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=2)

moviename = "23 - Nichts ist so wie es scheint"

metadata = parseMetadata(f"Videos\\{moviename}.txt")
print(metadata)

moviePoster = getMoviePoster(moviename, "imdb")
print(moviePoster)

metadata["poster"] = moviePoster
saveMetadata(f"{moviename}.json", metadata)
