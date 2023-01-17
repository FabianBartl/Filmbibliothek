
import requests, json, yaml, os
import urllib.parse

from pymediainfo import MediaInfo
from math import ceil
from bs4 import BeautifulSoup
from tqdm import tqdm
from colorama import Fore, Back, Style, init
init(autoreset=True)

# readout description from metadata file
def getDescFromFile(filename:str) -> dict:
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
		if ignoreError: return ""
		raise Exception(f"HTTP response code: {request.status_code}")
	html = BeautifulSoup(request.content, features="html.parser")

	page = html.find("a", attrs={"class": "ipc-metadata-list-summary-item__t"})
	if page is None:
		if ignoreError: return ""
		raise relImgNotFound
	pageURL = "https://www.imdb.com" + page.get("href")

	request = requests.get(pageURL, headers=header)
	if request.status_code != 200:
		if ignoreError: return ""
		raise Exception(f"HTTP response code: {request.status_code}")
	html = BeautifulSoup(request.content, features="html.parser")
	
	imgs = [ tag for tag in html.findAll("img", attrs={"class": "ipc-image"}) if tag.get("class") == ["ipc-image"] ]
	if imgs == []:
		if ignoreError: return ""
		raise relImgNotFound
	return imgs[0].get("srcset").split(", ")[-1].split(" ")[0]

# get metadata from imdb
def getMetadataFromIMDB(moviename:str, ignoreError:bool=False) -> dict:
	header = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36" ,"referer":"https://www.google.com/"}
	requestURL = "https://www.imdb.com/find/?q=" + urllib.parse.quote_plus(moviename)
	request = requests.get(requestURL, headers=header)
	if request.status_code != 200:
		if ignoreError: return {}
		raise Exception(f"HTTP response code: {request.status_code}")
	html = BeautifulSoup(request.content, features="html.parser")
	
	page = html.find("a", attrs={"class": "ipc-metadata-list-summary-item__t"})
	if page is None:
		if ignoreError: return {}
		raise Exception("Movie not found")
	
	metadata = {}
	metadata["imdb_id"] = page.get("href").split("/")[2]
	metadata["imdb_url"] = "https://www.imdb.com/title/"
	metadata["poster"] = getMoviePoster(moviename, "imdb")

	return metadata

# get metadata from user defined json file
def getUserDefMetadata(filename:str) -> dict:
	with open(filename, "r", encoding="utf-8") as file:
		metadata = yaml.safe_load(file)

	permitted_datafields = ["filename", "extension", "filepath", "directory", "movieID", "imdb_url", "duration"]
	for key in metadata:
		if key in permitted_datafields:
			del metadata[key]
	
	return metadata

# save collected metadata as json format
def saveMetadata(filename:str, metadata:dict) -> None:
	with open(filename, "w", encoding="utf-8") as file:
		json.dump(metadata, file, indent=2)

# run
def run(movie_directories:list[str]) -> None:
	metadata = {}
	movieID = 0
	for directoryNum, movie_directory in enumerate(movie_directories):

		for filename in tqdm(os.listdir(movie_directory), unit="File", desc=f"Scan directory '{movie_directory}'"):
			if not filename.lower().endswith((".mp4", ".mov", ".m4v", ".mkv")):
				continue

			movie_metadata = {}
			movie_metadata["filename"] = filename.rsplit(".", 1)[0]
			movie_metadata["extension"] = filename.rsplit(".", 1)[-1]
			movie_metadata["filepath"] = os.path.join(movie_directory, filename)
			movie_metadata["directory"] = movie_directory
			movie_metadata["title"] = movie_metadata["filename"]
			movie_metadata["movieID"] = str(movieID)
			
			info = MediaInfo.parse(movie_metadata["filepath"])
			track = info.video_tracks[0].to_data()
			if duration := track.get("duration"):
				seconds = int(float(duration)) // 1_000
				hours = int(seconds / 60 / 60)
				movie_metadata["duration"] = [hours, int(seconds/60 - hours*60)]
			if width := track.get("width"):
				width = float(width)
				# https://upload.wikimedia.org/wikipedia/commons/6/63/Vector_Video_Standards.svg
				if width <= 1200: movie_metadata["resolution"] = "VGA"
				elif width <= 1900: movie_metadata["resolution"] = "HD"
				elif width <= 3400: movie_metadata["resolution"] = "FullHD"
				elif width <= 5100: movie_metadata["resolution"] = "4K"
				elif width <= 7600: movie_metadata["resolution"] = "5K"
				else: movie_metadata["resolution"] = "8K"

			movie_metadata |= getMetadataFromIMDB(movie_metadata["title"], ignoreError=True)

			metadata_file = os.path.join(movie_directory, movie_metadata["filename"])
			if os.path.isfile(file := f"{metadata_file}.txt"):
				movie_metadata["description"] = getDescFromFile(file)
			if os.path.isfile(file := f"{metadata_file}.yml"):
				movie_metadata |= getUserDefMetadata(file)
			
			metadata[movieID] = movie_metadata
			movieID += 1
	
	saveMetadata(os.path.join("static", "data", "movies.json"), metadata)

# run with valid directory
if __name__ == "__main__":
	# load config from yaml file
	with open("config.yml", "r", encoding="utf-8") as file:
		config_yaml = yaml.safe_load(file)
	
	# get and check paths from config
	movie_directories = config_yaml.get("movie_directories")
	for i, movie_directory in enumerate(movie_directories):
		if not os.path.isdir(movie_directory):
			raise ValueError(f"Directory '{movie_directory}' not found")
		movie_directories[i] = os.path.abspath(movie_directory)
	run(movie_directories)
