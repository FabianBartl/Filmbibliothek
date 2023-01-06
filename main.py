
import json, os, re, sys

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
def getMoviePoster(moviename:str) -> bool:
    return False


metadata = parseMetadata(r"C:\Users\fabia\OneDrive\Dokumente\GitHub\video-library\Videos\23 - Nichts ist so wie es scheint.txt")
print(metadata)
