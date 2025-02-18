import os
from src.utils.read_geojson import read_geojson

geo_obj = read_geojson('./BR_Municipios_2023.json')
TOLERANCE = float(os.environ.get('TOLERANCE', 0.002))
BEATIFY_OUTPUT = bool(os.environ.get('BEATIFY_OUTPUT', False))
