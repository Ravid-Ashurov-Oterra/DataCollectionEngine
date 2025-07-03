import osmnx as ox
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely.prepared import prep
from h3.api.basic_str import cell_to_boundary
import math
from inputs.config import *
from inputs.osm_tags import *

def process_building_heights_and_assign_width(polygon, tile_ids, tiles_map):
    """
    Query building heights from OSM and assign the extracted or calculated height to function_dimensions.

    Args:
        polygon (Polygon): The bounding polygon for the area of interest.
        tile_ids (list): List of H3 tile IDs.
        tiles_map (dict): The dictionary mapping H3 tile IDs to their properties.

    Returns:
        None: Updates the `function_dimensions` in `tiles_map` in place.
    """

    print("Fetching building data...")
    try:
        # Query OSM for building features
        geo_data_frames = ox.features_from_polygon(polygon, tags=built_heights_tags)
        features = list(geo_data_frames.geometry)

        # Extract height and levels attributes
        geo_data_frames["height"] = geo_data_frames.get("height", None)
        geo_data_frames["levels"] = geo_data_frames.get("building:levels", None)

        print(f"Total building features: {len(features)}")

        # Create a union of all building geometries and prepare for intersection checks
        buildings_union = unary_union(features)
        buildings_prep = prep(buildings_union)

        # Iterate over H3 tiles and assign building heights to function_dimensions
        for h3_id in tile_ids:
            boundary = cell_to_boundary(h3_id)
            boundary_shapely = [(lng, lat) for lat, lng in boundary]
            h3_polygon = Polygon(boundary_shapely)

            # Check if the tile intersects with any building
            if buildings_prep.intersects(h3_polygon):
                building_height = DEFAULT_BUILDING_HEIGHT_M
                for idx, building in geo_data_frames.iterrows():
                    try:
                        if building.geometry.intersects(h3_polygon):
                            # Try to get the height or calculate it using levels
                            height = building.get("height")
                            levels = building.get("levels")

                            if height is not None and not math.isnan(float(height)):
                                building_height = float(height)
                            elif levels is not None and not math.isnan(float(levels)):
                                building_height = float(levels) * DEFAULT_LEVEL_HEIGHT_M
                    except Exception as e:
                        print(f"Error processing building feature {idx}: {e}, assigning default height.")
                        building_height = float(levels) * DEFAULT_LEVEL_HEIGHT_M

                # Assign the maximum height to function_dimensions
                tiles_map[h3_id]["function_dimensions"] = building_height

    except Exception as e:
        print(f"Error processing building heights: {e}")
