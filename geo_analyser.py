import json
import unicodedata
from shapely import Polygon, MultiPolygon, geometry, unary_union


TOLERANCE = 0.001


def read_geojson(path: str):
    with open(path, mode='r') as file:
        return json.loads(file.read())


def simplify_multipolygon(data: MultiPolygon):
    unified_multipolygon = unary_union(data)
    return unified_multipolygon.simplify(tolerance=TOLERANCE, preserve_topology=True)


def count_multipolygon(coordinates: list[list[list[int]]]):
    return sum([len(n[0]) for n in coordinates])


def normalize_text(data: str) -> str:
    normalized_text = unicodedata.normalize('NFD', data.strip().lower())
    return ''.join(char for char in normalized_text if unicodedata.category(char) != 'Mn')


geo_obj = read_geojson('./BR_Municipios_2023.json')


def main():
    search_name = input('>> ')

    for item in geo_obj['features']:
        city_name = item['properties']['NM_MUN']

        if normalize_text(city_name) == normalize_text(search_name):
            item_geometry = item['geometry']
            item_to_show = item.copy()
            item_to_show['geometry'] = '[...]'
            geo_type = item_geometry['type']
            skip_simplify = False
            is_multipolygon = False

            print(json.dumps(item_to_show, indent=2, ensure_ascii=False))

            save_geometry = input('\nsave geometry(S/N): ').lower().strip() == 's'

            if save_geometry:
                if geo_type == 'MultiPolygon':
                    print('multipolygons are too complex to simplify!')
                    want_simplify = input('\ndo you want try simplify(S/N): ').lower().strip() == 's'
                    skip_simplify = not want_simplify
                    is_multipolygon = True
                elif geo_type != 'Polygon':
                    print('Polygon not found!')
                    break


                print('saving...', end='\n\n')
                print(f'name: {city_name}')

                with open('output/' + city_name + '.json', 'w') as file:
                    if not is_multipolygon:
                        print(f'full coordinates count: {len(item_geometry['coordinates'][0])}')
                    else:
                        length = count_multipolygon(item_geometry['coordinates'])
                        print(f'full coordinates count: {length}')

                    file.write(json.dumps(item_geometry, indent=2))
                
                if not skip_simplify:
                    with open('output/' + city_name + '_simplified.json', 'w') as file:
                        coordinates = item_geometry['coordinates'][0]

                        polygon = None

                        if is_multipolygon:
                            polygon = simplify_multipolygon(MultiPolygon(item_geometry['coordinates']))
                        else:
                            polygon = Polygon(coordinates).simplify(tolerance=TOLERANCE, preserve_topology=True)

                        polygon_dict = geometry.mapping(polygon)
                        dict_coordinates = polygon_dict['coordinates']
                        length = count_multipolygon(dict_coordinates) if is_multipolygon else len(dict_coordinates[0])

                        print(f'simplified coordinates count: {length}')

                        file.write(json.dumps(polygon_dict, indent=2))
                
                print()

            break
    else:
        print('\ncity not found!\n')

if __name__ == '__main__':
    while True:
        try:
            main()
        except KeyboardInterrupt:
            print('\nexiting...')
            exit(0)
