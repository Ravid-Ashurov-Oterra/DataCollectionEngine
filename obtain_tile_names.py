import osmnx as ox
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely.prepared import prep
from h3.api.basic_str import cell_to_boundary
import re
from translation_utils import transliterate_arabic_name

# --- Helpers ---
def is_arabic(text):
    return bool(re.search(r'[\u0600-\u06FF]', text))

def transliterate_name(name):
    if not isinstance(name, str):
        return None
    return transliterate_arabic_name(name) if is_arabic(name) else name

def process_osm_names_and_assign_to_tiles(polygon, tile_ids, tiles_map):
    """
    Query OSM for feature names and assign them to intersecting tiles.

    Args:
        polygon (Polygon): The bounding polygon for the area of interest.
        tile_ids (list): List of H3 tile IDs.
        tiles_map (dict): The dictionary mapping H3 tile IDs to their properties.

    Returns:
        None: Updates the `name1` and `name2` fields in `tiles_map` in place.
    """
    # Tags to query OSM for named features
    name_tags = {
        "place": True,
        "highway": True,
        "natural": True,
        "landuse": True,
        "amenity": True,
        "building": True,
        "leisure": True,
        "shop": True,
        "tourism": True
    }

    print("Fetching OSM feature names...")
    try:
        # Query OSM for features with names
        geo_data_frames = ox.features_from_polygon(polygon, tags=name_tags)
        geo_data_frames = geo_data_frames[geo_data_frames["name"].notna()]  # Filter features with a name
        features = list(geo_data_frames.geometry)

        print(f"Total named features: {len(features)}")

        # Create a union of all named feature geometries and prepare for intersection checks
        named_features_union = unary_union(features)
        named_features_prep = prep(named_features_union)

        # Iterate over H3 tiles and assign names to intersecting tiles
        for h3_id in tile_ids:
            boundary = cell_to_boundary(h3_id)
            boundary_shapely = [(lng, lat) for lat, lng in boundary]
            h3_polygon = Polygon(boundary_shapely)

            # Check if the tile intersects with any named feature
            if named_features_prep.intersects(h3_polygon):
                for idx, feature in geo_data_frames.iterrows():
                    if feature.geometry.intersects(h3_polygon):
                        name = feature.get("name")
                        if name:
                            if tiles_map[h3_id]["name1"]:
                                tiles_map[h3_id]["name1"] += " / " + name
                            else:
                                tiles_map[h3_id]["name1"] = name
                            tiles_map[h3_id]["name2"] = transliterate_name(name)
                            break  # Assign the first matching name and stop
            else:
                # If no intersection, find the closest named feature
                closest_feature = None
                closest_distance = float('inf')
                for idx, feature in geo_data_frames.iterrows():
                    distance = h3_polygon.distance(feature.geometry)
                    if distance < closest_distance:
                        closest_distance = distance
                        closest_feature = feature

                if closest_feature is not None:
                    name = closest_feature.get("name")
                    if name:
                        tiles_map[h3_id]["name1"] = name
                        # tiles_map[h3_id]["name2"] = name
                        tiles_map[h3_id]["name2"] = transliterate_name(name)

    except Exception as e:
        print(f"Error processing OSM names: {e}")
