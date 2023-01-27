
import custom_logger
logger = custom_logger.init(__file__, log_to_console=False)
logger.debug(f"start of script: {__file__}")

import requests, json, yaml, os, urllib.parse, random
import user_agents
from scrapy.selector import Selector
from pymediainfo import MediaInfo
from bs4 import BeautifulSoup
from tqdm import tqdm
from colorama import Fore, Back, Style, init
logger.debug("init colorama")
init(autoreset=True)


# readout description from metadata file
def getDescFromFile(filename:str) -> dict:
	logger.debug(f"open {filename=}")
	with open(filename, "r", encoding="utf-8") as file:
		logger.debug(f"try: read-out readout description")
		try:
			# skip not relevant lines
			for _ in range(16):
				file.readline()
			logger.debug(f"16 lines scipped")

			# merge remaining lines as description
			logger.debug(f"read remaining lines")
			description = []
			while line := file.readline():
				if line.strip() == "": continue
				description.append(line.strip())
			logger.info(f"join {description=} with ' ' and return")
			return " ".join(description)
		
		# unexpected error
		except Exception as error:
			logger.error("failed to read description")
			logger.error(error)
			return None


# get metadata from Moviepilot
# https://www.moviepilot.de/movies/23-nichts-ist-so-wie-es-scheint
def getMetadatFromMoviepilot(moviename:str) -> dict:
	pass


# get metadata from imdb
def getMetadataFromIMDB(moviename:str, *, imdb_id:str=None) -> dict:
	logger.debug(f"get metadata for '{moviename}' from imdb")
	if not imdb_id:
		# request imdb search
		requestURL = "https://www.imdb.com/find/?q=" + urllib.parse.quote_plus(moviename)
		logger.debug(f"request url '{requestURL}'")
		response = requests.get(requestURL, headers=getUserAgent())
		logger.debug(response)
		if response.status_code != 200:
			logger.error(f"http response code: {response.status_code} for '{requestURL}'")
			return None
		logger.debug("parse html")
		html_bs4 = BeautifulSoup(response.content, features="html.parser")

		# for debugging only: store response
		if False:
			with open(f"logs/{moviename}_search.html", "wb+") as file:
				file.write(response.content)

		# get first search result
		page = html_bs4.find("a", attrs={"class": "ipc-metadata-list-summary-item__t"})
		if page is None:
			logger.error(f"no movie with title '{moviename}' found on imdb")
			return None
		
		# imdb id found by search
		imdb_id = page.get("href").split("/")[2]
		
	# collect metadata
	logger.debug("get imdb movie page")
	metadata = {}
	metadata["imdb-id"] = imdb_id
	logger.debug(f"imdb movie page: https://www.imdb.com/title/{metadata['imdb-id']}/")
	
	# request imdb movie page
	requestURL = f"https://www.imdb.com/title/{metadata['imdb-id']}/"
	logger.debug(f"request url '{requestURL}'")
	response = requests.get(requestURL, headers=getUserAgent())
	if response.status_code != 200:
		logger.error(f"http response code: {response.status_code} for '{requestURL}'")
		return None
	logger.debug("parse html")
	html_bs4 = BeautifulSoup(response.content, features="html.parser")
	html_scrap = Selector(text=response.content)

	# for debugging only: store response
	if False:
		with open(f"logs/{moviename}_page.html", "wb+") as file:
			file.write(response.content)
	
	# get poster
	logger.debug("get url of poster")
	if img := html_scrap.css("img[class=ipc-image]::attr(srcset)").get():
		poster = img.rsplit(", ",1)[-1].split(" ",1)[0]
		metadata["poster"] = poster
		logger.debug(f"{poster=}")
	else:
		logger.warning(f"poster of '{moviename}' not found")

	# get simple attributes
	attribute_xpaths = {
		"director": "//*[@id='__next']/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/div[3]/ul/li[1]/div/ul/li/a/text()",
		"writer": "//*[@id='__next']/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/div[3]/ul/li[2]/div/ul/li/a/text()",
		"year": "//*[@id='__next']/main/div/section[1]/section/div[3]/section/section/div[2]/div[1]/div/ul/li[1]/a/text()",
		"age-rating": "//*[@id='__next']/main/div/section[1]/section/div[3]/section/section/div[2]/div[1]/div/ul/li[2]/a/text()",
		"description": "//*[@id='__next']/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/div[1]/div[2]/span[3]/text()"
	}
	for attribute, xpath in attribute_xpaths.items():
		logger.debug(f"get {attribute}")
		if value := html_scrap.xpath(xpath).get():
			if attribute == "age-rating":
				value = f"ab {value}"
			metadata[attribute] = value
			logger.debug(f"{attribute}={value}")
		else:
			logger.warning(f"{attribute} of '{moviename}' not found")

	# get list attributes
	attribute_xpaths = {
		"main-cast": "//*[@id='__next']/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/div[3]/ul/li[3]/div/ul/li[{}]/a/text()",
		"genre": "//*[@id='__next']/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/div[1]/div[1]/div[2]/a[{}]/span/text()",
		"studio": "//*[@id='__next']/main/div/section[1]/div/section/div/div[1]/section[7]/div[2]/ul/li[6]/div/ul/li[{}]/a/text()"
	}
	for attribute, xpath in attribute_xpaths.items():
		logger.debug(f"get {attribute}")
		values = []
		i = 1
		while value := html_scrap.xpath(xpath.format(i)).get():
			values.append(value)
			i += 1
		if values != []:
			metadata[attribute] = values
			logger.debug(f"{attribute}={values}")
		else:
			logger.warning(f"{attribute} of '{moviename}' not found")

	# get imdb rating
	logger.debug(f"get imdb rating")
	if html_scrap.xpath("//*[@id='__next']/main/div/section[1]/section/div[3]/section/section/div[2]/div[2]/div/div[1]/a/div/div/div[2]").get():
		imdb_rating_points = html_scrap.xpath("//*[@id='__next']/main/div/section[1]/section/div[3]/section/section/div[2]/div[2]/div/div[1]/a/div/div/div[2]/div[1]/span[1]/text()").get()
		imdb_rating_votes = html_scrap.xpath("//*[@id='__next']/main/div/section[1]/section/div[3]/section/section/div[2]/div[2]/div/div[1]/a/div/div/div[2]/div[3]/text()").get()
		imdb_rating = {"imdb": {
			"points": imdb_rating_points.replace(".", ","),
			"votes": imdb_rating_votes.replace("K", "000").replace(".", "")
		}}
		metadata["rating"] = imdb_rating
		logger.debug(f"{imdb_rating=}")
	else:
		logger.warning(f"imdb rating of '{moviename}' not found")

	# TODO: get top cast with images

	logger.info(f"collect {metadata=} and return")
	return metadata


# get metadata from user defined json file
def getUserDefMetadata(filename:str) -> dict:
	logger.debug(f"open {filename=}")
	with open(filename, "r", encoding="utf-8") as file:
		logger.debug("safe load yaml file")
		metadata = yaml.safe_load(file)
		logger.debug(f"loaded {metadata=}")

	# remove permitted datafields
	permitted_datafields = ["filename", "extension", "filepath", "movie_directory", "metadata_directory", "movieID", "duration", "resolution"]
	logger.debug("iterate over metadate and remove permitted datafields")
	for key in metadata:
		if key in permitted_datafields:
			logger.warning(f"remove datafield '{key}' with '{metadata[key]}'")
			del metadata[key]

	logger.info(f"return {metadata=}")
	return metadata
	

# save collected metadata as json format
def saveMetadata(filename:str, metadata:dict) -> None:
	logger.debug(f"open {filename=}")
	with open(filename, "w+", encoding="utf-8") as file:
		logger.debug("dump json data")
		json.dump(metadata, file, indent=2)


# get random user agent
def getUserAgent(*, without_referer:bool=False) -> dict:
	user_agent = random.choice(user_agents.user_agents)
	referer = random.choice(user_agents.referers)
	logger.debug(f"{user_agent=} {referer=}")
	return {"user-agent": user_agent} | ({"referer": referer} if not without_referer else {})


# run
def run(movie_directories:list[str], metadata_directories:list[str]) -> None:
	metadata = {}
	movieID = 0
	logger.debug(f"iterate over {movie_directories=}")
	for directoryNum, (movie_directory, metadata_directory) in enumerate(zip(movie_directories, metadata_directories)):

		logger.debug(f"iterate over files in {movie_directory=}")
		for filename in tqdm(os.listdir(movie_directory), unit="File", desc=f"Scan directory {directoryNum+1}/{len(movie_directories)} '{movie_directory}'"):
			if not os.path.isfile(os.path.join(movie_directory, filename)):
				logger.warning(f"'{filename}' is not a file")
				continue
			if not filename.lower().endswith((".mp4", ".mov", ".m4v", ".mkv")):
				logger.warning(f"'{filename}' is not a movie")
				continue
			logger.info(f"'{filename}' is a movie file")

			# collect metadata from filepath
			logger.debug("collect metadata from filepath")
			movie_metadata = {}
			movie_metadata["filename"] = filename.rsplit(".", 1)[0]
			movie_metadata["extension"] = filename.rsplit(".", 1)[-1]
			movie_metadata["filepath"] = os.path.abspath(os.path.join(movie_directory, filename))
			movie_metadata["movie_directory"] = movie_directory
			movie_metadata["metadata_directory"] = metadata_directory
			movie_metadata["title"] = movie_metadata["filename"]
			movie_metadata["movieID"] = str(movieID)
			logger.debug(f"{movie_metadata=}")

			# collect metadata from file attributes
			logger.debug("try: collect metadata from file attributes")
			try:
				info = MediaInfo.parse(movie_metadata["filepath"])
				logger.debug("get video track data")
				track = info.video_tracks[0].to_data()
				# extract duration
				logger.debug("extract duration")
				if duration := track.get("duration"):
					seconds = int(float(duration)) // 1_000
					hours = int(seconds / 60 / 60)
					movie_metadata["duration"] = { "hours": hours, "minutes": int(seconds/60 - hours*60) }
					logger.debug(f"{duration=} {movie_metadata['duration']}")
				# extract resolution
				logger.debug("extract resolution")
				if width := track.get("width"):
					width = float(width)
					# https://upload.wikimedia.org/wikipedia/commons/6/63/Vector_Video_Standards.svg
					if width <= 1200: movie_metadata["resolution"] = "VGA"
					elif width <= 1900: movie_metadata["resolution"] = "HD"
					elif width <= 3400: movie_metadata["resolution"] = "FullHD"
					elif width <= 5100: movie_metadata["resolution"] = "4K"
					elif width <= 7600: movie_metadata["resolution"] = "5K"
					else: movie_metadata["resolution"] = "8K"
					logger.debug(f"{width=} {movie_metadata['resolution']=}")
			except:
				logger.error(f"failed to collect metadata from file attributes")

			# preload user-defined metadata, but apply them later
			metadata_file = os.path.join(metadata_directory, movie_metadata["filename"])
			user_defined_metadata = getUserDefMetadata(file) if os.path.isfile(file := f"{metadata_file}.yml") else {}
			
			# get additional metadata
			if user_defined_metadata.get("scrape-additional-data", True):
				# scrape from imdb
				logger.debug("get metadata from imdb")
				if imdb_metadata := getMetadataFromIMDB(user_defined_metadata.get("title", movie_metadata["title"]), imdb_id=user_defined_metadata.get("imdb-id")):
					movie_metadata |= imdb_metadata
					logger.debug("metadata from imdb scraped")
			else:
				logger.debug("scraping of additional data is not wanted")

			logger.debug(f"get metadata from local files: {metadata_file=}")
			# get description from mediathek-view file
			if os.path.isfile(file := f"{metadata_file}.txt"):
				logger.debug("get description from mediathek-view file")
				if description := getDescFromFile(file):
					movie_metadata["description"] = getDescFromFile(file)
					logger.debug(f"{description=}")
			# get metadata from user-defined YAML file
			if os.path.isfile(file := f"{metadata_file}.yml"):
				logger.debug("get metadata from user-defined yaml file")
				movie_metadata |= user_defined_metadata

			logger.info(f"add movie with {movieID=} and {movie_metadata=}")
			metadata[movieID] = movie_metadata
			movieID += 1
	
	# save metadata
	movies_json_path = os.path.abspath(os.path.join("static", "data", "movies.json"))
	logger.debug(f"store metadata of all movies in '{movies_json_path}'")
	saveMetadata(movies_json_path, metadata)
	logger.info(f"metadata of all movies in '{movies_json_path}' stored")


# run with valid directory
if __name__ == "__main__":
	msg_closeAndRunAgain = lambda: input(Style.BRIGHT + "Press Enter to close, then run the script again.")

	# load config from yaml file
	logger.debug("load config.yml")
	with open("config.yml", "r", encoding="utf-8") as file:
		config_yaml = yaml.safe_load(file)
		logger.info("config.yml loaded")
	
	# update logging level
	log_level = custom_logger.level_to_int(config_yaml.get("log-level"))
	logger.setLevel(log_level)
	logger.info(f"update logger lever to {log_level}")
	
	# get and check paths from config
	# movie-directories:
	logger.debug(f"load movie directories from config.yml")
	movie_directories = config_yaml.get("movie-directories", [])
	if movie_directories == [] or movie_directories == "" or movie_directories == None:
		logger.error("no movie directories configured")
		print(Fore.RED + f"No movie directories configured")
		print(Fore.YELLOW + "Please add your movie directories to the config.yml file.")
		msg_closeAndRunAgain()
		exit(1)

	if not type(movie_directories) is list:
		logger.debug(f"convert single movie directory string to list: {movie_directories=}")
		movie_directories = [ movie_directories ]
		logger.debug(f"as list: {movie_directories=}")
	
	logger.debug("check validity of movie directories")
	for i, movie_directory in enumerate(movie_directories):
		if not os.path.isdir(movie_directory):
			logger.error(f"directory {movie_directory=} not found")
			print(Fore.RED + f"Directory '{movie_directory}' not found")
			print(Fore.YELLOW + "Please use valid absolute paths as movie directory.")
			msg_closeAndRunAgain()
			exit(1)
		movie_directories[i] = os.path.abspath(movie_directory)
		logger.debug(f"valid movie directory: {movie_directory=} {movie_directories[i]=}")

	# metadata-directories:
	logger.debug(f"load metadata directories from config.yml")
	metadata_directories = config_yaml.get("metadata-directories", [])
	if metadata_directories == [] or metadata_directories == "" or metadata_directories == None:
		logger.error("no metadata directories configured")
		print(Fore.RED + f"No metadata directories configured")
		print(Fore.YELLOW + "Please add your metadata directories to the config.yml file.")
		msg_closeAndRunAgain()
		exit(1)

	if not type(metadata_directories) is list:
		logger.debug(f"convert single movie directory string to list: {metadata_directories=}")
		metadata_directories = [ metadata_directories ]
		logger.debug(f"as list: {metadata_directories=}")

	logger.debug("check validity of metadata directories")
	for i, metadata_directory in enumerate(metadata_directories):
		if not os.path.isdir(metadata_directory):
			logger.error(f"directory {metadata_directory=} not found")
			print(Fore.RED + f"Directory '{metadata_directory}' not found")
			print(Fore.YELLOW + "Please use valid absolute paths as movie directory.")
			msg_closeAndRunAgain()
			exit(1)
		metadata_directories[i] = os.path.abspath(metadata_directory)
		logger.debug(f"valid metadata directory: {metadata_directory=} {metadata_directories[i]=}")

	if len(metadata_directories) != len(movie_directories):
		logger.error(f"the length of the metadata directories (={len(metadata_directories)}) does not match the length of the movie directories (={len(movie_directories)})")
		print(Fore.RED + f"The length of the metadata directories (={len(metadata_directories)}) needs to match with the length of the movie directories (={len(movie_directories)})")
		msg_closeAndRunAgain()
		exit(1)

	# run
	logger.debug(f"collect metadata with {movie_directories=} {metadata_directories=}")
	run(movie_directories, metadata_directories)
	logger.info("movie data collected and stored")
	print(Fore.GREEN + "Movie data collected and stored")

logger.debug(f"end of script: {__file__}")
