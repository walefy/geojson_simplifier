import json
from shapely import Polygon, geometry


def read_geojson(path: str):
    with open(path, mode='r') as file:
        return json.loads(file.read())


geo_obj = read_geojson('./BR_Municipios_2023.json')


def main():
    search_name = input('>> ').strip().lower()

    for item in geo_obj['features']:
        city_name = item['properties']['NM_MUN'].strip().lower()

        if city_name == search_name:
            item_geometry = item['geometry']
            item['geometry'] = '[...]'

            print(json.dumps(item, indent=2, ensure_ascii=False))

            save_geometry = input('\nsave geometry(S/N): ').lower().strip() == 's'

            if save_geometry:
                print('saving...', end='\n\n')
                print(f'name: {city_name}')

                with open('output/' + city_name + '.json', 'w') as file:
                    print(f'full coordinates count: {len(item_geometry['coordinates'][0])}')

                    file.write(json.dumps(item_geometry, indent=2))
                
                with open('output/' + city_name + '_simplified.json', 'w') as file:
                    coordinates: list[list[int]] = item_geometry['coordinates'][0]

                    polygon = Polygon(coordinates).simplify(tolerance=0.01, preserve_topology=True)
                    polygon_dict = geometry.mapping(polygon)
                    simplified_coordinates = polygon_dict['coordinates'][0]

                    print(f'simplified coordinates count: {len(simplified_coordinates)}')

                    file.write(json.dumps(polygon_dict, indent=2))
                
                print()

            break

if __name__ == '__main__':
    while True:
        try:
            main()
        except KeyboardInterrupt:
            print('\nexiting...')
            exit(0)
