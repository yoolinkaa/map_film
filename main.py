""" movies map """

import argparse
import folium
from geopy.geocoders import Nominatim
from haversine import haversine

parser = argparse.ArgumentParser()
parser.add_argument('year', type = str)
parser.add_argument('latitude', type = float)
parser.add_argument('longtitude', type = float)
parser.add_argument('path', type = str)
args = parser.parse_args()

def read_file(dir: str, year: str, names = False) -> list:
    """
    read file
    return a list of places where the filem was made
    if names = True
    return a list of filems names
    """
    lst_of_coord = []
    with open(dir, 'r') as locations:
        while True:
            line = locations.readline()
            if not line:
                break
            if '(' in line and str(year) in line:
                elem = line.split('\t')
                for i in elem:
                    if names and '\"' in i and i and '#' in i:
                        lst_of_coord += [i]
                    elif '(' not in i and '\"' not in i and i and not names:
                        lst_of_coord += [i]
        return [i.rstrip() for i in lst_of_coord]

def get_coordinates(place: str) -> list:
    """
    return coordinates of place
    >>> get_coordinates('Nashville, Tennessee, USA')
    [36.1622767, -86.7742984]
    """
    geolocator = Nominatim(user_agent="HTTP")
    location = geolocator.geocode(place)
    try:
        return [location.latitude, location.longitude]
    except AttributeError:
        return False

def distance(my_loc: list, dist: list):
    """
    return distanse between two locations
    """
    return haversine(my_loc, get_coordinates(dist))

def first_ten_places(dir: str, loc: list, year: str) -> list:
    """
    get firt 10 places locatet the closest to loc
    return tuple: place, distance, film
    """
    places = []
    names = []
    for i, j in enumerate(read_file(dir, year)):
        if get_coordinates(j):
            places += [j]
            names += [read_file(dir, year, names = True)[i]]
    dist = [distance(loc, get_coordinates(i)) for i in places]
    lst = list(zip(places, dist, names))
    res = sorted(lst, key = lambda x: x[1])
    return res[:10]

def create_map(dir: list, loc: list, year: str):
    """
    main function that create an HTML map
    """
    places = first_ten_places(dir, loc, year)
    map = folium.Map(tiles = 'Stamen Terrain')
    fg_films = folium.FeatureGroup (name="Films map")
    fg_circle = folium.FeatureGroup (name = 'Circle')
    map.add_child(folium.Marker(location = loc,
                            popup="Your location",
                            icon=folium.Icon('orange')))
    for place in places:
        fg_films.add_child(folium.Marker(location = get_coordinates(place[0]),
                            popup = place[2],
                            icon = folium.Icon()))
        fg_circle.add_child(folium.CircleMarker(location = get_coordinates(place[0]),
                            radius = 10,
                            fill_col = 'yellow',
                            color = 'red',
                            popup = place[2]))
    map.add_child(fg_films)
    map.add_child(fg_circle)
    map.add_child(folium.LayerControl())
    map.save('films_locations.html')
    map

if __name__ == '__main__':
    year = args.year
    lat = args.latitude
    lon = args.longtitude
    location = [lat, lon]
    path = args.path
    create_map(path, location, year)
