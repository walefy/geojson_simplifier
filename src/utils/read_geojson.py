import json

def read_geojson(path: str):
    with open(path, mode='r') as file:
        return json.loads(file.read())
