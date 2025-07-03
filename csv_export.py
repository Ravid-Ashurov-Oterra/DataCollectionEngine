import os
from datetime import datetime
import csv

def export_tiles_map_to_csv(tiles_map, filename_prefix="tiles_map"):
    """
    Exports the tiles_map dictionary to a CSV file.

    Args:
        tiles_map (dict): The dictionary containing tile data.
        filename_prefix (str): The prefix for the output CSV file name.
    """
    # Generate a timestamped filename
    output_dir = "../Outputs/CSVs"
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{output_dir}/{filename_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    # Define the fields to export
    fieldnames = ['id', 'center', 'neighbors', 'height', 
                  'score1', 'score2', 'tile_function', 'dynamics', 'function_dimensions', 'name1', 'name2']
    
    # Write the data to a CSV file
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for tile_id, tile_data in tiles_map.items():
            writer.writerow(tile_data)
    
    print(f"Wrote {len(tiles_map)} rows to {filename}")