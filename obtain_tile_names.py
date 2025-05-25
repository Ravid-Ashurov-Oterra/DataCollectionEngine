import osmnx as ox
from shapely.geometry import Polygon
from arabic_buckwalter_transliteration.transliteration import arabic_to_buckwalter
from shapely.ops import unary_union
from shapely.prepared import prep
from h3.api.basic_str import cell_to_boundary
import re

# --- Helpers ---
def is_arabic(text):
    return bool(re.search(r'[\u0600-\u06FF]', text))

def transliterate_name(name):
    if not isinstance(name, str):
        return None
    return arabic_to_buckwalter(name) if is_arabic(name) else name

def process_osm_names_and_assign_to_tiles(polygon, tile_ids, tiles_map):
    """
    Query OSM for feature names and assign them to intersecting tiles.

    Args:
        polygon (Polygon): The bounding polygon for the area of interest.
        tile_ids (list): List of H3 tile IDs.
        tiles_map (dict): The dictionary mapping H3 tile IDs to their properties.

    Returns:
        None: Updates the `tile_name` and `tile_name_translit` fields in `tiles_map` in place.
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
                            tiles_map[h3_id]["tile_name"] = name
                            tiles_map[h3_id]["tile_name_translit"] = transliterate_name(name)
                            break  # Assign the first matching name and stop

    except Exception as e:
        print(f"Error processing OSM names: {e}")
