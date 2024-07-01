import googlemaps
import itertools
from typing import List, Tuple, Optional
from geopy.distance import geodesic

# Replace with your actual Google Maps API key
API_KEY = 'YOUR_GOOGLE_MAPS_API_KEY'

# Initialize the Google Maps client
gmaps = googlemaps.Client(key=API_KEY)

def load_coordinates() -> List[Tuple[float, float]]:
    # Load your 100 coordinates here
    coordinates = [
        (37.7749, -122.4194), # Example coordinate
        # Add other coordinates here
    ]
    return coordinates

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
    
    for subset in itertools.combinations(coords, num_points):
        subset = [start] + list(subset)
        total_distance = sum(
            geodesic(subset[i], subset[i+1]).miles for i in range(len(subset) - 1)
        )
        if abs(total_distance - max_distance) < abs(best_distance - max_distance):
            best_distance = total_distance
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

def main():
    coords = load_coordinates()
    fixed_start = (37.7749, -122.4194)  # Replace with your actual start coordinate
    max_distance = 10  # 10 miles
    num_points = 9  # 9 points plus the fixed start point make 10

    best_subset = find_subsets_with_fixed_start(coords, fixed_start, max_distance, num_points)
    if best_subset is None:
        print("No valid route found.")
        return

    route = get_route(best_subset)
    if route and check_start_end_proximity(route):
        print("Route found with the following coordinates:")
        for step in route[0]['legs'][0]['steps']:
            print(step['start_location'], step['end_location'])
    else:
        print("No valid route found that meets the start and end proximity requirement.")

if __name__ == "__main__":
    main()
