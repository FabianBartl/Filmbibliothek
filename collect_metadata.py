
import requests, json, sys, os
import urllib.parse
from bs4 import BeautifulSoup
from tqdm import tqdm

# readout metadata file and store it as dictionary
def parseMetadataFromFile(filename:str) -> dict:
	metadata = {}

	with open(filename, "r", encoding="utf-8") as file:
		metadata["channel"] = file.readline()
		metadata["topic"] = file.readline()
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
def getMoviePoster(moviename:str, source:str="imdb", ignoreError=False) -> str:
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
		if ignoreError:
			return ""
		raise Exception(f"HTTP response code: {request.status_code}")
	html = BeautifulSoup(request.content, features="html.parser")

	if source == "amazon":
		img = html.find("img", attrs={"alt": moviename})
		if img is None:
			if ignoreError:
				return ""
			raise relImgNotFound
		return img.get("data-src")
	
	elif source == "bing":
		imgs = [ tag for tag in html.findAll(attrs={"class": "iusc"}) if tag.get("class") == ["iusc"] ]
		if imgs == []:
			if ignoreError:
				return ""
			raise relImgNotFound

		imgURL = [ param.replace("mediaurl=", "") for param in imgs[0].get("href").split("&") if param.startswith("mediaurl=") ]
		if imgURL == []:
			if ignoreError:
				return ""
			raise relImgNotFound
		return urllib.parse.unquote(imgURL[0])

	elif source == "google":
		pass

	elif source == "ebay":
		pass

	elif source == "imdb":
		page = html.find("a", attrs={"class": "ipc-metadata-list-summary-item__t"})
		if page is None:
			if ignoreError:
				return ""
			raise relImgNotFound
		pageURL = "https://www.imdb.com" + page.get("href")

		request = requests.get(pageURL, headers=header)
		if request.status_code != 200:
			if ignoreError:
				return ""
			raise Exception(f"HTTP response code: {request.status_code}")
		html = BeautifulSoup(request.content, features="html.parser")
		
		imgs = [ tag for tag in html.findAll("img", attrs={"class": "ipc-image"}) if tag.get("class") == ["ipc-image"] ]
		if imgs == []:
			if ignoreError:
				return ""
			raise relImgNotFound
		return imgs[0].get("srcset").split(", ")[-1].split(" ")[0]

# get metadata from imdb
def getMetadataFromIMDB(moviename:str, ignoreError=False) -> dict:
	header = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36" ,"referer":"https://www.google.com/"}

	requestURL = "https://www.imdb.com/find/?q="+urllib.parse.quote_plus(moviename)
	request = requests.get(requestURL, headers=header)
	if request.status_code != 200:
		if ignoreError:
			return {}
		raise Exception(f"HTTP response code: {request.status_code}")
	html = BeautifulSoup(request.content, features="html.parser")
	
	page = html.find("a", attrs={"class": "ipc-metadata-list-summary-item__t"})
	if page is None:
		if ignoreError:
			return {}
		raise Exception("Movie not found")
	
	metadata = {}
	metadata["imdb_id"] = page.get("href").split("/")[2]
	metadata["imdb_url"] = f"https://www.imdb.com/title/" + metadata["imdb_id"]
	metadata["poster"] = getMoviePoster(moviename, "imdb")

	requestURL = metadata["imdb_url"] + "/fullcredits/"
	request = requests.get(requestURL, headers=header)
	if request.status_code != 200:
		if ignoreError:
			return {}
		raise Exception(f"HTTP response code: {request.status_code}")
	html = BeautifulSoup(request.content, features="html.parser")

	metadata["credits_html"] = html.find(id="fullcredits_content").__repr__()
	return metadata

# save collected metadata as json format
def saveMetadata(filename:str, metadata:dict) -> None:
	with open(filename, "w", encoding="utf-8") as file:
		json.dump(metadata, file, indent=2)

# cli
if __name__ == "__main__":
	movie_directory = os.path.abspath( sys.argv[1] if len(sys.argv) >= 2 else "movies" )
	movies_json = os.path.abspath( sys.argv[2] if len(sys.argv) >= 3 else os.path.join("static", "movies.json") )
	
	metadata = {}
	movieID = 0
	for filename in tqdm(os.listdir(movie_directory), unit="File", desc="Progress"):
		if not filename.endswith(".mp4"):
			continue

		movie_metadata = {}
		movie_metadata["filename"] = ".".join(filename.split(".")[:-1])
		movie_metadata["extension"] = filename.split(".")[-1]
		movie_metadata["filepath"] = os.path.join(movie_directory, filename)
		movie_metadata["directory"] = movie_directory
		movie_metadata["title"] = movie_metadata["filename"]
		movie_metadata["movieID"] = str(movieID)

		metadata_file = os.path.join(movie_directory, movie_metadata["filename"]+".txt")
		if os.path.isfile(metadata_file):
			movie_metadata |= parseMetadataFromFile(metadata_file)
		movie_metadata |= getMetadataFromIMDB(movie_metadata["title"], ignoreError=True)
		
		metadata[movieID] = movie_metadata
		movieID += 1
	
	saveMetadata(movies_json, metadata)
