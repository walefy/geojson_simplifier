import json
import unicodedata
from shapely import Polygon, MultiPolygon, geometry, unary_union

from src.data.data import geo_obj, TOLERANCE
from src.data.geojson import GeoJson


def simplify_multipolygon(data: MultiPolygon):
    unified_multipolygon = unary_union(data)
    return unified_multipolygon.simplify(tolerance=TOLERANCE, preserve_topology=True)


def count_multipolygon(coordinates: list[list[list[int]]]):
    return sum([len(n[0]) for n in coordinates])


def normalize_text(data: str) -> str:
    normalized_text = unicodedata.normalize('NFD', data.strip().lower())
    return ''.join(char for char in normalized_text if unicodedata.category(char) != 'Mn')


def find_city_geometry(geo_obj, search_name: str):
    for item in geo_obj['features']:
        city_name = item['properties']['NM_MUN']
        if normalize_text(city_name) == normalize_text(search_name):
            return item, city_name
    return None, None


def build_polygon_geojson(item_geometry: dict) -> tuple[GeoJson, int]:
    return GeoJson(type="Feature", geometry=item_geometry), len(item_geometry["coordinates"][0])


def build_simplified_geojson(item_geometry: dict) -> tuple[GeoJson, int]:
    coordinates = item_geometry['coordinates'][0]
    polygon = Polygon(coordinates).simplify(tolerance=TOLERANCE, preserve_topology=True)

    polygon_dict = geometry.mapping(polygon)
    dict_coordinates = polygon_dict['coordinates']
    length = len(dict_coordinates[0])

    return GeoJson(type="Feature", geometry=polygon_dict), length


def build_multipolygon_geojson(item_geometry: dict) -> tuple[GeoJson, int]:
    length = count_multipolygon(item_geometry['coordinates'])

    return GeoJson(type="Feature", geometry=item_geometry), length


def build_simplified_multipolygon(item_geometry: dict) -> tuple[GeoJson, int]:
    polygon = simplify_multipolygon(MultiPolygon(item_geometry['coordinates']))

    polygon_dict = geometry.mapping(polygon)
    dict_coordinates = polygon_dict['coordinates']
    length = count_multipolygon(dict_coordinates)

    return GeoJson(type="Feature", geometry=polygon_dict), length


def save_polygon_geometry(city_name: str, item_geometry: dict):
    print('saving...', end='\n\n')
    print(f'name: {city_name}')

    with open(f'output/{city_name}.json', 'w') as file:
        geojson, length = build_polygon_geojson(item_geometry)
        print(f'full coordinates count: {length}')

        file.write(str(geojson))

    with open(f'output/{city_name}_simplified.json', 'w') as file:
        geojson, length = build_simplified_geojson(item_geometry)
        print(f'simplified coordinates count: {length}')

        file.write(str(geojson))


def save_multipolygon_geometry(city_name: str, item_geometry: dict):
    print('saving...', end='\n\n')
    print(f'name: {city_name}')

    with open(f'output/{city_name}.json', 'w') as file:
        geojson, length = build_multipolygon_geojson(item_geometry)
        print(f'full coordinates count: {length}')

        file.write(str(geojson))

    with open(f'output/{city_name}_simplified.json', 'w') as file:
        geojson, length = build_simplified_multipolygon(item_geometry)
        print(f'simplified coordinates count: {length}')

        file.write(str(geojson))


def process_city_geometry(geo_obj, search_name: str):
    item, city_name = find_city_geometry(geo_obj, search_name)
    if not item:
        print('\ncity not found!\n')
        return

    item_geometry = item['geometry']
    item_to_show = item.copy()
    item_to_show['geometry'] = '[...]'
    geo_type = item_geometry['type']
 
    print(json.dumps(item_to_show, indent=2, ensure_ascii=False))

    save_geometry_flag = input('\nsave geometry(S/N): ').lower().strip() == 's'

    if save_geometry_flag:
        if (not isinstance(city_name, str)):
            raise ValueError('city name not found')

        match geo_type:
            case 'MultiPolygon':
                save_multipolygon_geometry(city_name, item_geometry)
            case 'Polygon':
                save_polygon_geometry(city_name, item_geometry)
            case _:
                print('Polygon not found!')
                return

def main():
    search_name = input('>> ')
    process_city_geometry(geo_obj, search_name)


if __name__ == '__main__':
    while True:
        try:
            main()
        except KeyboardInterrupt:
            print('\nexiting...')
            exit(0)
