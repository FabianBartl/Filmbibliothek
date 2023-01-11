
import requests, json, sys, os
import urllib.parse
from bs4 import BeautifulSoup
from tqdm import tqdm
from colorama import Fore, Back, Style, init
init(autoreset=True)

# readout description from metadata file
def getDescriptionFromFile(filename:str) -> dict:
	with open(filename, "r", encoding="utf-8") as file:
		for _ in range(16):
			file.readline()

		description = []
		while line := file.readline():
			if line.strip() == "": continue
			description.append(line.strip())
		return " ".join(description)

# get movie poster as url
def getMoviePoster(moviename:str, ignoreError:bool=False) -> str:
	relImgNotFound = Exception("Related image not found")

	header = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36" ,"referer":"https://www.google.com/"}
	requestURL = "https://www.imdb.com/find/?q=" + urllib.parse.quote_plus(moviename)
	request = requests.get(requestURL, headers=header)
	if request.status_code != 200:
		if ignoreError:
			return ""
		raise Exception(f"HTTP response code: {request.status_code}")
	html = BeautifulSoup(request.content, features="html.parser")

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
def getMetadataFromIMDB(moviename:str, ignoreError:bool=False) -> dict:
	header = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36" ,"referer":"https://www.google.com/"}
	requestURL = "https://www.imdb.com/find/?q=" + urllib.parse.quote_plus(moviename)
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
	metadata["imdb_url"] = "https://www.imdb.com/title/" + metadata["imdb_id"]
	metadata["poster"] = getMoviePoster(moviename, "imdb")

	return metadata

# get metadata from user defined json file
def getMetadataFromFile(filename:str) -> dict:
	with open(filename, "r", encoding="utf-8") as file:
		metadata = json.load(file)

	permitted_datafields = ["filename", "extension", "filepath", "directory", "movieID"]
	for key in metadata:
		if key in permitted_datafields:
			del metadata[key]
	
	return metadata

# save collected metadata as json format
def saveMetadata(filename:str, metadata:dict) -> None:
	with open(filename, "w", encoding="utf-8") as file:
		json.dump(metadata, file, indent=2)

# run
def run(movie_directory:str) -> None:
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

		movie_metadata |= getMetadataFromIMDB(movie_metadata["title"], ignoreError=True)

		metadata_file = os.path.join(movie_directory, movie_metadata["filename"])
		if os.path.isfile(file := f"{metadata_file}.txt"):
			movie_metadata["description"] = getDescriptionFromFile(file)
		if os.path.isfile(file := f"{metadata_file}.json"):
			movie_metadata |= getMetadataFromFile(file)
		
		metadata[movieID] = movie_metadata
		movieID += 1
	
	saveMetadata(os.path.join("static", "data", "movies.json"), metadata)

# run with valid directory
if __name__ == "__main__":
	# get and check path from command line parameter
	if len(sys.argv) >= 2:
		if os.path.isdir(sys.argv[1]):
			run(os.path.abspath(sys.argv[1]))
			exit()
		raise ValueError("Directory not found")
	
	# request correct path from user input
	while not os.path.isdir(movie_directory := input("Movie directory: ")):
		print(Fore.RED + "Directory not found\n")
	run(os.path.abspath(movie_directory))
