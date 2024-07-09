import googlemaps
import itertools
import requests
from typing import List, Tuple, Optional
from geopy.distance import geodesic
from datetime import datetime
from dotenv import load_dotenv
import os

now = datetime.now().strftime("%Y%m%d%H%M%S")
os.makedirs(f'generations/{now}', exist_ok=True)

# load .env file
load_dotenv()

API_KEY = os.getenv('API_KEY')
gmaps = googlemaps.Client(key=API_KEY)

def calculate_distance_matrix(coords: List[Tuple[float, float]]) -> List[List[float]]:
    distances = []
    for origin in coords:
        row = []
        for destination in coords:
            row.append(geodesic(origin, destination).miles)
        distances.append(row)
    return distances

def find_subsets_with_fixed_start(coords: List[Tuple[float, float]], start: Tuple[float, float], max_distance: float, num_points: int) -> Optional[List[Tuple[float, float]]]:
    best_subset = None
    best_distance = float('inf')
    best_equidistance = float('inf')
    
    for subset in itertools.combinations(coords, num_points):
        subset = [start] + list(subset)
        total_distance = sum(
            geodesic(subset[i], subset[i+1]).miles for i in range(len(subset) - 1)
        )
        if abs(total_distance - max_distance) < abs(best_distance - max_distance):
            distances = [geodesic(subset[i], subset[i+1]).miles for i in range(len(subset) - 1)]
            equidistance = max(distances) - min(distances)
            if equidistance < best_equidistance:
                best_distance = total_distance
                best_equidistance = equidistance
                best_subset = subset
                
    return best_subset

def get_route(coords: List[Tuple[float, float]]) -> Optional[dict]:
    if len(coords) < 2:
        return None
    waypoints = coords[1:-1]
    directions_result = gmaps.directions(coords[0], coords[-1], waypoints=waypoints)
    return directions_result if directions_result else None

def check_start_end_proximity(route: dict) -> bool:
    start = route[0]['legs'][0]['start_location']
    end = route[0]['legs'][-1]['end_location']
    distance = geodesic((start['lat'], start['lng']), (end['lat'], end['lng'])).miles
    return distance <= 1

def produce_map_image(route: dict, waypoints: List[Tuple[float, float]]) -> None:
    markers = '|'.join([f'{lat},{lng}' for lat, lng in waypoints])
    
    url = f"https://maps.googleapis.com/maps/api/staticmap?size=800x600&path=enc:{route[0]['overview_polyline']['points']}&markers=color:blue|{markers}&key={API_KEY}"
    response = requests.get(url)

    # Save the image
    with open(f'generations/{now}/map.png', 'xb') as file:
        file.write(response.content)

    print('Map image saved!')

def get_total_distance(route: dict) -> float:
    total_distance_meters = 0
    for leg in route["legs"]:
        total_distance_meters += leg["distance"]["value"]
    # Convert distance to kilometers
    total_distance_miles = (total_distance_meters / 1000) * 0.621371 # convert to km then miles
    return total_distance_miles

def main():
    coords = [
        (41.93268379724611, -87.64066266841367), # Willie Lill's
        (41.932400857739275, -87.657889541256), # Delilah's
        (41.923477211369914, -87.6458730394061), # Halligan Bar
        (41.91843924544154, -87.63876926812834), # River Shannon
        (41.91137715228922, -87.6351703136166), # Old Town Ale House
        (41.91179627660367, -87.63754917977109), # Sedgwick Stop
        (41.93817470294708, -87.6710943658501), # Cody's Public House
        (41.937444540948576, -87.65939643999876), # Will's Northwoods Inn
        (41.94295883033523, -87.6694055403165), # The Green Lady
        (41.93156205499557, -87.65502890041141), # Racine Plumbing
        (41.945799726069936, -87.65176733423068), # Graystone Tavern
        (41.94896098210485, -87.65455189497676), # Murphy's Bleachers
        (41.942129473243185, -87.65292366325524), # Sheffield's
        (41.95021758314778, -87.65805604896123), # Gman Tavern
        (41.90389581442262, -87.6298928974373), # The Lodge
        (41.91841042610322, -87.65251956407256), # Kincade's
        (41.90919866657256, -87.63371825639283), # Burton Place
        (41.89395607586084, -87.63038086923366), # Mom's Place
        (41.89191870370212, -87.63065327248435), # Fado Irish Pub
        (41.8911552877815, -87.64635692078011), # Richard's Bar
        (41.94335698789769, -87.67490893361825), # Four Moon Tavern
        (41.92540146429915, -87.6786753984117), # Leavitt Street Inn
        (41.90779971006246, -87.67191575289937), # Ina Mae
        (41.91125878667242, -87.67827629701215), # Gracie O'Malley's
        (41.89700271137983, -87.62584231281137), # Streeter's Tavern
    ]
    FIXED_START = os.getenv('FIXED_START')
    fixed_start = (FIXED_START.split(',')[0], FIXED_START.split(',')[1])  # Replace with your actual start coordinate
    max_distance = 10  # 10 miles
    num_points = 6  # 6 stops

    best_subset = find_subsets_with_fixed_start(coords, fixed_start, max_distance, num_points)
    if best_subset is None:
        print("No valid route found.")
        return
    else:
        print("Best subset found:", best_subset)

    route = get_route(best_subset)
    if route and check_start_end_proximity(route):
        print("Route found with <1 mile start and end proximity!")
    else:
        print("Start and end not within 1 mile of each other!")

    print("Route found with the following coordinates:")
    for step in route[0]['legs'][0]['steps']:
        print(step['start_location'], step['end_location'])

    with open(f'generations/{now}/route.json', 'x') as f:
        f.write(str(route))

    print(get_total_distance(route))

    produce_map_image(route, best_subset)

if __name__ == "__main__":
    main()
