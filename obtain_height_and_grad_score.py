from shapely.geometry import Polygon, mapping
from h3 import grid_disk
from h3.api.basic_str import cell_to_boundary
import rasterio
import numpy as np
import pyproj
from shapely.ops import transform as shapely_transform
from rasterio.mask import mask
from inputs.config import *

def soften_tile_heights(tiles_map, tile_ids, disk_k=2):
    """
    Soften the height values of tiles by averaging with their neighbors.

    Args:
        tiles_map (dict): The dictionary containing tile data.
        tile_ids (list): List of H3 tile IDs.
        disk_k (int): The strength of the softening, determines the radius of neighbors to consider.

    Returns:
        None: Updates the `tile_height` in `tiles_map` in place.
    """
    for h3_id in tile_ids:
        # Skip tiles with tile_function values in the NO_SOFTEN_TILE_FUNCTIONS list
        if tiles_map[h3_id]['tile_function'] in NO_SOFTEN_TILE_FUNCTIONS:
            continue

        # Get neighbors' heights within the specified disk radius
        neighbors_heights = []
        for neighbor_id in grid_disk(h3_id, disk_k):
            if neighbor_id in tiles_map and tiles_map[neighbor_id] is not None and tiles_map[neighbor_id]['hard_height'] is not None:
                neighbors_heights.append(tiles_map[neighbor_id]['hard_height'])

        # Calculate average height
        if len(neighbors_heights) > 0:
            avg_height = (tiles_map[h3_id]['hard_height'] + sum(neighbors_heights)) / len(neighbors_heights)
            tiles_map[h3_id]['tile_height'] = avg_height

def process_tile_heights(tif_paths_with_functions, tile_ids, tiles_map, softening_disk_k=2):
    """
    Process tile heights using multiple GeoTIFF files and update the tiles_map with height data based on tile_function.

    Args:
        tif_paths_with_functions (dict): A dictionary where keys are GeoTIFF file paths and values are lists of tile_function values.
        tile_ids (list): List of H3 tile IDs.
        tiles_map (dict): The dictionary mapping H3 tile IDs to their properties.
        softening_disk_k (int): The strength of the softening, determines the radius of neighbors to consider.

    Returns:
        None: Updates the `tile_height` in `tiles_map` in place.
    """
    tiles_height_count = 0

    for tif_path, functions in tif_paths_with_functions.items():
        with rasterio.open(tif_path) as topographic_data:
            raster_crs = topographic_data.crs
            project = pyproj.Transformer.from_crs("EPSG:4326", raster_crs, always_xy=True).transform

            for h3_id in tile_ids:
                # Only process tiles with matching tile_function
                if tiles_map[h3_id]['tile_function'] not in functions:
                    continue

                boundary = cell_to_boundary(h3_id)
                boundary_shapely = [(lng, lat) for lat, lng in boundary]
                h3_polygon = Polygon(boundary_shapely)

                # Re-project to raster CRS
                h3_poly_proj = shapely_transform(project, h3_polygon)
                try:
                    out_image, out_transform = mask(topographic_data, [mapping(h3_poly_proj)], crop=True)

                    # Convert each band to uint32 for math
                    r = out_image[0].astype(np.uint32)
                    g = out_image[1].astype(np.uint32)
                    b = out_image[2].astype(np.uint32)

                    elevation = (0.299* r) + (0.587* g) + (0.114* b)
                    # elevation = r
                    masked = np.ma.masked_equal(elevation, topographic_data.nodata)

                    if masked.count() > 0:
                        avg_height = round(float(masked.mean()), 2)
                        # Assign the height to the tile
                        tiles_map[h3_id]['hard_height'] = avg_height
                        tiles_map[h3_id]['tile_height'] = avg_height
                        tiles_height_count += 1

                except Exception as e:
                    print(f"Skipping H3 cell {h3_id} due to error: {e}")

    # Soften the heights
    soften_tile_heights(tiles_map, tile_ids, disk_k=softening_disk_k)

    # Clean up the tiles_map by removing the hard_height key
    for h3_id in tile_ids:
        if 'hard_height' in tiles_map[h3_id]:
            del tiles_map[h3_id]['hard_height']

    print(f"Total tiles with height: {tiles_height_count}")

def calculate_gradient_scores(tiles_map, tile_ids):
    """
    Calculate gradient scores for tiles based on the height difference with their neighbors,
    while avoiding tiles with tile_function values in NO_SOFTEN_TILE_FUNCTIONS.

    Args:
        tiles_map (dict): The dictionary containing tile data.
        tile_ids (list): List of H3 tile IDs.

    Returns:
        None: Updates the `tile_grad_score` in `tiles_map` in place.
    """
    max_height_diff = 0

    for h3_id in tile_ids:
        # Skip tiles with tile_function values in NO_SOFTEN_TILE_FUNCTIONS
        if tiles_map[h3_id]['tile_function'] in NO_SOFTEN_TILE_FUNCTIONS:
            continue

        # Get neighbors' heights
        neighbors_heights = []
        for neighbor_id in tiles_map[h3_id]['tile_neighbors']:
            if (
                neighbor_id in tiles_map and
                tiles_map[neighbor_id] is not None and
                tiles_map[neighbor_id]['tile_height'] is not None and
                tiles_map[neighbor_id]['tile_function'] not in NO_SOFTEN_TILE_FUNCTIONS
            ):
                neighbors_heights.append(tiles_map[neighbor_id]['tile_height'])

        # Calculate gradient score
        if len(neighbors_heights) > 0:
            height_diff = abs(tiles_map[h3_id]['tile_height'] - max(neighbors_heights))
            if height_diff > max_height_diff:
                max_height_diff = height_diff
            tiles_map[h3_id]['tile_grad_score'] = height_diff

    # Normalize gradient score (values between 0 and 1, based on max height difference)
    for h3_id in tile_ids:
        if max_height_diff > 0:  # Avoid division by zero
            tiles_map[h3_id]['tile_grad_score'] = round(tiles_map[h3_id]['tile_grad_score'] / max_height_diff, 2)
