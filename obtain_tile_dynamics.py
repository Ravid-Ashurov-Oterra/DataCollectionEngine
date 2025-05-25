import osmnx as ox
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely.prepared import prep
from h3.api.basic_str import cell_to_boundary

def process_tags_and_append_dynamics(tags_and_dynamics, polygon, tile_ids, tiles_map):
    """
    Process multiple tags and append values to the tile_dynamics field for tiles that intersect with the features.

    Args:
        tags_and_dynamics (list): A list of [tags_dict, dynamic_value] pairs.
        polygon (Polygon): The bounding polygon for the area of interest.
        tile_ids (list): List of H3 tile IDs.
        tiles_map (dict): The dictionary mapping H3 tile IDs to their properties.

    Returns:
        None: Updates the `tile_dynamics` in `tiles_map` in place.
    """
    # Prepare a dictionary to store prepared geometries for each dynamic value
    prepped_features = {}

    # Create prep objects for each tag set
    for tags, dynamic_value in tags_and_dynamics:
        print(f"Fetching data for dynamic value: {dynamic_value}...")
        try:
            geo_data_frames = ox.features_from_polygon(polygon, tags=tags)
            features = list(geo_data_frames.geometry)
            print(f"Total features for {dynamic_value}: {len(features)}")

            # Create a union of all features and prepare it for intersection checks
            features_union = unary_union(features)
            prepped_features[dynamic_value] = prep(features_union)
        except Exception as e:
            print(f"Error processing {dynamic_value}: {e}, skipping.")
            continue

    # Iterate over H3 tiles and append dynamics for intersecting features
    for h3_id in tile_ids:
        boundary = cell_to_boundary(h3_id)
        boundary_shapely = [(lng, lat) for lat, lng in boundary]
        h3_polygon = Polygon(boundary_shapely)

        # Check intersections for all dynamic values
        for dynamic_value, features_prep in prepped_features.items():
            if features_prep.intersects(h3_polygon):
                tiles_map[h3_id]['tile_dynamics'].append(dynamic_value)

def mark_flood_risk_tiles(tiles_map, tile_ids, flood_risk_percentage=0.02):
    """
    Mark the lowest percentage of tiles as flood risk based on their height.

    Args:
        tiles_map (dict): The dictionary containing tile data.
        tile_ids (list): List of H3 tile IDs.
        flood_risk_percentage (float): The percentage of tiles to mark as flood risk.

    Returns:
        None: Updates the `tile_dynamics` in `tiles_map` in place.
    """
    # Sort tiles by height
    sorted_tiles = sorted(tile_ids, key=lambda x: tiles_map[x]['tile_height'])
    num_flood_risk_tiles = int(len(sorted_tiles) * flood_risk_percentage)

    for i in range(num_flood_risk_tiles):
        h3_id = sorted_tiles[i]
        tiles_map[h3_id]['tile_dynamics'].append("FLOODED")
