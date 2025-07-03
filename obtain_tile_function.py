import osmnx as ox
from shapely.geometry import Polygon, mapping
from shapely.ops import unary_union
from shapely.prepared import prep
from h3.api.basic_str import cell_to_boundary
import math
from inputs.config import *

def process_multiple_tags(tags_and_functions, polygon, tile_ids, tiles_map):
    """
    Process multiple tags and update tiles_map with intersections for all tile functions.

    Args:
        tags_and_functions (list): A list of [tags_dict, tile_function] pairs.
        polygon (Polygon): The bounding polygon for the area of interest.
        tile_ids (list): List of H3 tile IDs.
        tiles_map (dict): The dictionary mapping H3 tile IDs to their properties.
    """
    # Prepare a dictionary to store prepared geometries for each tile_function
    prepped_features = {}

    # Create prep objects for each tag set
    for tags, tile_function in tags_and_functions:
        print(f"fetching {tile_function} data...")
        try: 
            geo_data_frames = ox.features_from_polygon(polygon, tags=tags)
            features = list(geo_data_frames.geometry)
            print(f"Total features for {tile_function}: {len(features)}")

            # Create a union of all features and prepare it for intersection checks
            features_union = unary_union(features)
            prepped_features[tile_function] = prep(features_union)
        except Exception as e:
            print(f"Error processing {tile_function}: {e}, skipping.")
            continue

    # Iterate over H3 tiles once and check for intersections with all feature types
    tiles_with_functions_count = {tile_function: 0 for _, tile_function in tags_and_functions}

    for h3_id in tile_ids:
        boundary = cell_to_boundary(h3_id)
        boundary_shapely = [(lng, lat) for lat, lng in boundary]
        h3_polygon = Polygon(boundary_shapely)

        # Check intersections for all tile functions
        for tile_function, features_prep in prepped_features.items():
            if features_prep.intersects(h3_polygon):
                tiles_with_functions_count[tile_function] += 1
                tiles_map[h3_id]['tile_function'] = tile_function

    # Print summary of results
    for tile_function, count in tiles_with_functions_count.items():
        print(f"Total tiles with {tile_function}: {count}")

def tags_to_osmnx_filter(tags_dict):
    """
    Convert a dictionary of OSM tags to an OSMnx custom filter string.
    
    Parameters:
    -----------
    tags_dict : dict
        Keys are OSM tag keys, values determine the matching:
        - str: exact match
        - list: multiple possible values (OR)
        - True: tag exists
        - False: tag doesn't exist
        - dict with 'regex' key: custom regex pattern
    
    Returns:
    --------
    str: Overpass QL filter string for osmnx.graph.graph_from_polygon()
    
    Examples:
    ---------
    >>> tags_to_osmnx_filter({"highway": ["residential", "service"]})
    '["highway"~"residential|service"]'
    >>> tags_to_osmnx_filter({"highway": "primary", "name": True})
    '["highway"="primary"]["name"]'
    """
    filters = []
    
    for key, value in tags_dict.items():
        if isinstance(value, list):
            filters.append(f'["{key}"~"{"|".join(str(v) for v in value)}"]')
        elif isinstance(value, dict) and 'regex' in value:
            filters.append(f'["{key}"~"{value["regex"]}"]')
        elif value is True:
            filters.append(f'["{key}"]')
        elif value is False:
            filters.append(f'[!"{key}"]')
        else:
            filters.append(f'["{key}"="{value}"]')
    
    return "".join(filters)

def process_roads_and_assign_width(polygon, tile_ids, tiles_map, roads_tags):
    try:
        # Generate custom filter for roads
        roads_custom_filter = tags_to_osmnx_filter(roads_tags)

        # Fetch road network graph and convert to GeoDataFrame
        roads_system_graph = ox.graph_from_polygon(polygon, custom_filter=roads_custom_filter)
        print(roads_system_graph)
        roads_geo_data_frames = ox.graph_to_gdfs(roads_system_graph, nodes=False)
        roads = list(roads_geo_data_frames.geometry)

        # Fetch road features with additional attributes (e.g., width, lanes)
        _roads = ox.features_from_polygon(polygon, tags=roads_tags)
        roads_with_width_data = {}

        # Loop through each road in the GeoDataFrame
        for idx, road in _roads.iterrows():
            # Try to get the width or calculate it based on lanes
            width = road.get('width')
            lanes = road.get('lanes')

            if (width is not None and not math.isnan(float(width))) or (lanes is not None and not math.isnan(float(lanes))):
                if isinstance(idx, tuple):
                    element_type, osmid = idx
                    estimated_width = 0
                    if width is not None and not math.isnan(float(width)):
                        estimated_width = float(width)
                    else:
                        estimated_width = float(lanes) * LANE_WIDTH_M

                    roads_with_width_data[osmid] = {
                        'geometry': road.geometry,
                        'width': estimated_width
                    }

        # Create a union of all road geometries and prepare for intersection checks
        roads_union = unary_union(roads)
        roads_prep = prep(roads_union)

        # Iterate over H3 tiles and assign road functions and widths
        tiles_with_roads_count = 0
        for h3_id in tile_ids:
            boundary = cell_to_boundary(h3_id)
            boundary_shapely = [(lng, lat) for lat, lng in boundary]
            h3_polygon = Polygon(boundary_shapely)

            # Check if the tile intersects with any road
            has_road = roads_prep.intersects(h3_polygon)

            if has_road:
                tiles_with_roads_count += 1
                tiles_map[h3_id]['tile_function'] = 'road'

                # Try to assign the maximum road width
                max_width = 0
                for road in roads_with_width_data.values():
                    if road['geometry'].intersects(h3_polygon):
                        max_width = max(max_width, road['width'])

                if max_width > 0:
                    tiles_map[h3_id]['function_dimensions'] = max_width

        print(f"Total tiles with roads: {tiles_with_roads_count}")

    except ValueError as e:
        print(f"Error processing roads: {e}. Skipping road processing for this polygon.")
