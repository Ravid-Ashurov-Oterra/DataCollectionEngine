from shapely.geometry import Polygon
from h3 import h3shape_to_cells, LatLngPoly, cell_to_latlng, grid_ring

# internal  
from inputs.osm_tags import *
from inputs.config import *
from obtain_tile_function import process_multiple_tags, process_roads_and_assign_width
from obtain_tile_dynamics import process_tags_and_append_dynamics, mark_flood_risk_tiles
from obtain_height_and_grad_score import process_tile_heights, calculate_gradient_scores
from csv_export import export_tiles_map_to_csv
from obtain_tile_dim import process_building_heights_and_assign_width
from obtain_tile_names import process_osm_names_and_assign_to_tiles

# Create bounding box Polygon (lng, lat)
# -----------------------------------------
polygon = Polygon([
    (BOUNDING_BOX['west'], BOUNDING_BOX['south']),
    (BOUNDING_BOX['east'], BOUNDING_BOX['south']),
    (BOUNDING_BOX['east'], BOUNDING_BOX['north']),
    (BOUNDING_BOX['west'], BOUNDING_BOX['north']),
    (BOUNDING_BOX['west'], BOUNDING_BOX['south'])
])
res15Poly = Polygon([
    (ZOOM_IN_BBOX['west'], ZOOM_IN_BBOX['south']),
    (ZOOM_IN_BBOX['east'], ZOOM_IN_BBOX['south']),
    (ZOOM_IN_BBOX['east'], ZOOM_IN_BBOX['north']),
    (ZOOM_IN_BBOX['west'], ZOOM_IN_BBOX['north']),
    (ZOOM_IN_BBOX['west'], ZOOM_IN_BBOX['south'])  
])

# Convert to H3-compatible LatLngPoly (lat, lng)
# -------------------------------------------------
outer = [(lat, lng) for lng, lat in res15Poly.exterior.coords]
if outer[0] != outer[-1]:
    outer.append(outer[0])
latlng_poly = LatLngPoly(outer)

# Get H3 tiles and init structure
# ----------------------------------
tile_ids = h3shape_to_cells(latlng_poly, H3_RES)
tile_count = len(tile_ids)
print(f"H3 tiles count: {tile_count}")
# Initialize a hash (dictionary) with each tile_id mapped to an empty object
tiles_map = {tile_id: {
    'tile_h3_id': tile_id,
    'tile_center': cell_to_latlng(tile_id),
    'tile_neighbors': set(grid_ring(tile_id, 1)) - {tile_id},
    'tile_function': 'na',  
    'tile_height': None, 
    'tile_grad_score': 0, 
    'tile_dynamics': [],  
    'tile_dimensions': 0.0, 
    'hard_height': 0,
    'tile_name': '',
    'tile_name_translit': '',
} for tile_id in tile_ids}


tags_and_functions = [
    [buildings_tags, 'built'],
    [vegetation_tags, 'veg'],
    [parks_tags, 'park'],
    [schools_tags, 'school'],
    [religion_tags, 'religious'],
    [amenities_tags, 'amenity'],
    [water_tags, 'water'],
]
process_multiple_tags(tags_and_functions, polygon, tile_ids, tiles_map)
process_roads_and_assign_width(polygon, tile_ids, tiles_map, roads_tags)
tif_paths_with_functions = {
    "../Assets/dtm_clip.tif": ["na", "road", "veg", "park", "built", "school", "religious", "amenity", "water", "food"],
}
process_tile_heights(tif_paths_with_functions, tile_ids, tiles_map, SOFTENING_STRENGTH)
tags_and_dynamics = [
    [food_tags, "FOOD"],
    [government_tags, 'GOV']
]
process_tags_and_append_dynamics(tags_and_dynamics, polygon, tile_ids, tiles_map)
process_building_heights_and_assign_width(polygon, tile_ids, tiles_map)
calculate_gradient_scores(tiles_map, tile_ids)
mark_flood_risk_tiles(tiles_map, tile_ids)
process_osm_names_and_assign_to_tiles(polygon, tile_ids, tiles_map)
export_tiles_map_to_csv(tiles_map)