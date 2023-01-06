
from bs4 import BeautifulSoup
import requests

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
    if source == "amazon":
        header = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36" ,"referer":"https://www.google.com/"}
        request = requests.get(f"https://www.amazon.de/s?k={moviename}", headers=header)

        if request.status_code != 200:
            raise Exception(f"HTTP response code: {request.status_code}")
        
        html = BeautifulSoup(request.content, features="html.parser")
        img = html.body.find(attr={"alt": moviename})

        if img is None:
            raise Exception("Related image not found")

        return img.get("data-src")
    
    elif source == "bing":
        pass
    
    raise ValueError(f"unknow source: {source}")


metadata = parseMetadata(r"C:\Users\fabia\OneDrive\Dokumente\GitHub\video-library\Videos\23 - Nichts ist so wie es scheint.txt")
print(metadata)

moviePoster = getMoviePoster("23 - Nichts ist so wie es scheint")
print(moviePoster)

