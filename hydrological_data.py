import numpy as np
import geopandas as gpd
import rasterio
import matplotlib.pyplot as plt
from skimage.draw import polygon
from skimage.transform import resize
import scipy.io as sio
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

helpers_folder = os.path.join(current_dir, 'helpers')

def get_path(file_name):
    return os.path.join(helpers_folder, file_name)

def process_hydrological_data(rainfall_path):
    # Load DEM and shapefile
    with rasterio.open(get_path('reprojected.tif')) as src:
        DEM = src.read(1).astype(float)  # Load DEM as float to handle NaN
        R_dem = src
        mask = np.zeros(DEM.shape, dtype=bool)

    # Read shapefile and create mask
    S = gpd.read_file(get_path('real_shape file.shp'))
    for shape in S.geometry:
        if shape.is_empty or not shape.is_valid:
            continue

        x_world, y_world = shape.exterior.xy
        cols = np.round((np.array(x_world) - R_dem.bounds.left) / R_dem.res[0]).astype(int)
        rows = np.round((R_dem.bounds.top - np.array(y_world)) / R_dem.res[1]).astype(int)

        is_finite = np.isfinite(cols) & np.isfinite(rows)
        cols, rows = cols[is_finite], rows[is_finite]

        if len(cols) < 3 or len(rows) < 3:
            continue

        rr, cc = polygon(rows, cols, mask.shape)
        mask[rr, cc] = True

    DEM[~mask] = np.nan  # Set areas outside mask to NaN

    # Crop DEM and mask to mask bounds
    row_indices, col_indices = np.where(mask)
    min_row, max_row = row_indices.min(), row_indices.max()
    min_col, max_col = col_indices.min(), col_indices.max()

    cropped_DEM = DEM[min_row:max_row + 1, min_col:max_col + 1]

    # Save cropped DEM
    transform = R_dem.transform * rasterio.Affine.translation(min_col, min_row)
    with rasterio.open(get_path('cropped_dem.tif'), 'w', driver='GTiff', height=cropped_DEM.shape[0], 
                       width=cropped_DEM.shape[1], count=1, dtype=cropped_DEM.dtype,
                       crs=R_dem.crs, transform=transform) as dst:
        dst.write(cropped_DEM, 1)

    # Flow direction calculation
    DEM_filled = np.nan_to_num(cropped_DEM)
    flow_direction = np.zeros(DEM_filled.shape)

    dx = [1, 1, 0, -1, -1, -1, 0, 1]
    dy = [0, -1, -1, -1, 0, 1, 1, 1]

    for row in range(1, DEM_filled.shape[0] - 1):
        for col in range(1, DEM_filled.shape[1] - 1):
            max_slope, max_direction = -np.inf, 0
            center_elevation = DEM_filled[row, col]
            
            for k in range(8):
                neighbor_row, neighbor_col = row + dy[k], col + dx[k]
                neighbor_elevation = DEM_filled[neighbor_row, neighbor_col]
                slope = center_elevation - neighbor_elevation

                if slope > max_slope:
                    max_slope, max_direction = slope, k
            
            flow_direction[row, col] = 2 ** max_direction

    sio.savemat(get_path("direction_map.mat"), {"flowdirection": flow_direction})

    # Flow accumulation
    accumulation = np.zeros(flow_direction.shape)
    
    for row in range(1, flow_direction.shape[0] - 1):
        for col in range(1, flow_direction.shape[1] - 1):
            direction = flow_direction[row, col]
            if direction == 1 and col + 1 < flow_direction.shape[1]:
                accumulation[row, col + 1] += 1
            elif direction == 2 and row - 1 >= 0 and col + 1 < flow_direction.shape[1]:
                accumulation[row - 1, col + 1] += 1
            elif direction == 4 and row - 1 >= 0:
                accumulation[row - 1, col] += 1
            elif direction == 8 and row - 1 >= 0 and col - 1 >= 0:
                accumulation[row - 1, col - 1] += 1
            elif direction == 16 and col - 1 >= 0:
                accumulation[row, col - 1] += 1
            elif direction == 32 and row + 1 < flow_direction.shape[0] and col - 1 >= 0:
                accumulation[row + 1, col - 1] += 1
            elif direction == 64 and row + 1 < flow_direction.shape[0]:
                accumulation[row + 1, col] += 1
            elif direction == 128 and row + 1 < flow_direction.shape[0] and col + 1 < flow_direction.shape[1]:
                accumulation[row + 1, col + 1] += 1

    sio.savemat(get_path("accumulation_map.mat"), {"accumulation": accumulation})

    # Load rainfall data and crop
    with rasterio.open(rainfall_path) as src:
        rainfall_data = src.read(1).astype(float)

    rainfall_data = resize(rainfall_data, DEM.shape, mode='reflect', anti_aliasing=True)
    rainfall_data = rainfall_data[min_row:max_row + 1, min_col:max_col + 1]

    # Load runoff data
    runoff_data = rasterio.open(get_path('runoff.tif')).read(1).astype(float)

    if runoff_data.shape != rainfall_data.shape:
        rainfall_data = resize(rainfall_data, runoff_data.shape, mode='reflect', anti_aliasing=True)

    runoff_data[runoff_data < 1e-3] = 0
    rainfall_data_in_inches = rainfall_data * 0.03937
    rainfall_data_in_inches_per_hour = rainfall_data_in_inches / 8760
    cell_area_in_acres = abs(runoff_data.shape[1] * runoff_data.shape[0]) / 4046.86
    discharge_data = runoff_data * rainfall_data_in_inches_per_hour * cell_area_in_acres
    discharge_data[discharge_data < 0] = 0

    # Save discharge data as GeoTIFF
    with rasterio.open(get_path('discharge_map.tif'), 'w', driver='GTiff', height=discharge_data.shape[0], 
                       width=discharge_data.shape[1], count=1, dtype=discharge_data.dtype,
                       crs=R_dem.crs, transform=R_dem.transform) as dst:
        dst.write(discharge_data, 1)

    # Total inflow from discharge data
    total_inflow = np.nansum(discharge_data) * 1000
    print(f'Total Reservoir Inflow: {total_inflow:.2f} inches acres per hour')
    return total_inflow
# Example usage
info =  process_hydrological_data('rainfall.tif')
print(info)