import pandas as pd

def merge_h3_csv_files(file1, file2, output_file):
    """
    Merge two CSV files containing H3 tile data based on specified logic.

    Args:
        file1 (str): Path to the first CSV file.
        file2 (str): Path to the second CSV file.
        output_file (str): Path to save the merged CSV file.
    """
    # Load the CSV files into DataFrames
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)

    # Define the function weights (ascending order)
    function_weights = {
        'water': 1,
        'amenity': 2,
        'religious': 3,
        'school': 4,
        'veg': 5,
        'park': 6,
        'built': 7,
        'road': 8
    }

    # Merge the two DataFrames on the 'tile_h3_id' column
    merged = pd.merge(df1, df2, on='tile_h3_id', how='outer', suffixes=('_file1', '_file2'))

    # Apply the merging logic
    merged['tile_center'] = merged['tile_center_file1']  # Always take from the first file
    merged['tile_neighbors'] = merged['tile_neighbors_file1']  # Always take from the first file
    merged['tile_dimensions'] = merged[['tile_dimensions_file1', 'tile_dimensions_file2']].max(axis=1)  # Take max value
    merged['tile_height'] = merged['tile_height_file1'].combine_first(merged['tile_height_file2'])  # Prefer first file
    merged['tile_grad_score'] = merged['tile_grad_score_file1'].combine_first(merged['tile_grad_score_file2'])  # Prefer first file

    # Merge 'tile_dynamics' by combining distinct values from both files
    def merge_tile_dynamics(row):
      dynamics1 = row['tile_dynamics_file1']
      dynamics2 = row['tile_dynamics_file2']

      # Convert to sets to handle distinct values
      set1 = set(eval(dynamics1)) if pd.notna(dynamics1) and dynamics1 != "[]" else set()
      set2 = set(eval(dynamics2)) if pd.notna(dynamics2) and dynamics2 != "[]" else set()

      # Combine the sets and convert back to a comma-separated string
      merged_dynamics = str(sorted(set1.union(set2)))
      return merged_dynamics

    merged['tile_dynamics'] = merged.apply(merge_tile_dynamics, axis=1)

    # Resolve 'tile_function' based on weights
    def resolve_function(row):
        func1 = row['tile_function_file1']
        func2 = row['tile_function_file2']
  
        # Handle cases where func1 or func2 is NaN
        if pd.isna(func1) or func1 == 'na':
            return func2
        if pd.isna(func2) or func2 == 'na':
            return func1

        # Check if func1 and func2 exist in function_weights, assign default weight if not
        weight1 = function_weights.get(func1, 0)  # Default weight is 0 if func1 is not in function_weights
        weight2 = function_weights.get(func2, 0)  # Default weight is 0 if func2 is not in function_weights

        if(weight1 ==0):
          print(f"Unknown function in file1: '{func1}'")
        if(weight2 ==0): 
          print(f"Unknown function in file2: '{func2}'")

        # Compare weights and return the function with the higher weight
        return func1 if weight1 >= weight2 else func2

    merged['tile_function'] = merged.apply(resolve_function, axis=1)

    # Select the final columns to save
    final_columns = ['tile_h3_id', 'tile_center', 'tile_neighbors', 'tile_height', 
                    'tile_grad_score', 'tile_function', 'tile_dynamics', 'tile_dimensions', 'tile_name', 'tile_name_translit']
    merged = merged[final_columns]

    # Save the merged DataFrame to a new CSV file
    merged.to_csv(output_file, index=False)
    print(f"Merged file saved to {output_file}")


file1 = '../data/mergeAssets/tiles_map_20250520_091358.csv' 
file2 = '../data/mergeAssets/NablusTileTable-20_05.csv'  
output_file = '../data/mergeAssets/merged_tiles.csv' 
merge_h3_csv_files(file1, file2, output_file)