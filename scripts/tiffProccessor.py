import rasterio
import numpy as np

# Path to your topographic GeoTIFF
tif_path = "dtm_clip.tif"

with rasterio.open(tif_path) as dataset:
    # Read metadata
    print("CRS:", dataset.crs)
    print("Bounds:", dataset.bounds)
    print("Resolution:", dataset.res)
    print("Width, Height:", dataset.width, dataset.height)
    print("Number of Bands:", dataset.count)
    print("Data type:", dataset.dtypes)
    print("Descriptions:", dataset.descriptions)
    print("NoData value:", dataset.nodata)
    print("Tag:", dataset.tags())
    print("Tags[1]:", dataset.tags(1))
    print("Tags[2]:", dataset.tags(2))
    print("Tags[3]:", dataset.tags(3))
    print("SCALE:", dataset.scales)
    print("Add offset:", dataset.offsets)
    print("UNIT", dataset.units)

    # Read the elevation data (assuming it's the first band)
    elevation = dataset.read(1)

    # Check some stats
    print("Min elevation:", np.min(elevation))
    print("Max elevation:", np.max(elevation))

    # Check a sample pixel from each band
    sample_row, sample_col = 100, 100
    for i in range(1, dataset.count + 1):
        band_data = dataset.read(i)
        print(f"Band {i} sample value:", band_data[sample_row, sample_col])
    
    # Print min/max per band
    for i in range(1, dataset.count + 1):
        band = dataset.read(i)
        print(f"Band {i} - min: {band.min()}, max: {band.max()}")
