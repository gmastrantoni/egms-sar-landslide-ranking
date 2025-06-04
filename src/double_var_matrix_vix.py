#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 13 15:39:16 2024

@author: giandomenico
"""

import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

def calculate_percentiles(data, bins):
    """Calculate percentile bins for the data."""
    percentiles = np.percentile(data, np.linspace(0, 100, bins + 1))
    # Use 'right=False' to include the right edge in the last bin
    bin_indices = np.digitize(data, percentiles, right=False)
    # Ensure the highest value fits in the last bin
    bin_indices = np.where(bin_indices > bins, bins, bin_indices)
    return bin_indices - 1  # adjust indices to be zero-indexed

def get_color_mix(value1, value2):
    """Blend two colors based on attribute values."""
    # Define base colors for each attribute scale
    color_scale1 = np.array([
        [247, 252, 253],  # light blue
        [224, 236, 244],
        [191, 211, 230],
        [158, 188, 218],
        [107, 174, 214],
        [66, 146, 198],
        [33, 113, 181],
        # [8, 81, 156],
        # [8, 48, 107]       # dark blue
    ]) / 255.0  # Normalize RGB

    color_scale2 = np.array([
        [255, 245, 240],  # light pink
        [254, 224, 210],
        [252, 187, 161],
        [252, 146, 114],
        [251, 106, 74],
        [239, 59, 44],
        [203, 24, 29],
        # [165, 15, 21],
        # [103, 0, 13]       # dark red
    ]) / 255.0  # Normalize RGB

    # Interpolate colors within each scale
    color1 = color_scale1[int(value1 * (len(color_scale1) - 1))]
    color2 = color_scale2[int(value2 * (len(color_scale2) - 1))]

    # Return the average of the two colors
    return np.mean([color1, color2], axis=0)

def plot_bivariate_colors(shapefile, attribute1, attribute2, bins=3):
    # Load the shapefile
    gdf = gpd.read_file(shapefile)
    
    # Ensure the attributes exist
    if attribute1 not in gdf.columns or attribute2 not in gdf.columns:
        raise ValueError("Specified attributes do not exist in the shapefile.")

    # Calculate the bins for each attribute
    gdf['bin1'] = calculate_percentiles(gdf[attribute1], bins)
    gdf['bin2'] = calculate_percentiles(gdf[attribute2], bins)

    # Generate bivariate color map
    cmap = np.zeros((bins, bins, 3))
    for i in range(bins):
        for j in range(bins):
            cmap[i, j] = get_color_mix(i / (bins - 1), j / (bins - 1))

    # Create a new column for colors
    gdf['color'] = gdf.apply(lambda row: cmap[int(row['bin1']), int(row['bin2'])], axis=1)

    # Plotting
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6), gridspec_kw={'width_ratios': [3, 1]})
    
    # Plot the map
    gdf.plot(ax=ax1, color=[tuple(color) for color in gdf['color']], edgecolor='black', linewidth=1.0)
    ax1.set_title(f'Bivariate Color Plot of {attribute1} and {attribute2}')
    ax1.set_axis_off()

    # Create the legend on a separate subplot
    for i in range(bins):
        for j in range(bins):
            ax2.add_patch(mpatches.Rectangle((j, i), 1, 1, facecolor=cmap[i, j]))

    ax2.set_xlim(0, bins)
    ax2.set_ylim(0, bins)
    ax2.set_xticks([])
    ax2.set_yticks([])
    ax2.set_xlabel(f'{attribute2} (Low to High)')
    ax2.set_ylabel(f'{attribute1} (Low to High)')
    ax2.set_title("Legend")
    plt.show()



# Example usage
shapefile_path = '/Users/giandomenico/Documents/SAPIENZA/AR/regione_lazio/dati/RESULTS_EGMS_BASIC_MODEL/ASC/DATACLUSTER_ASC_RESIZED.shp'  # Update with the path to your shapefile
plot_bivariate_colors(shapefile_path, 'vel_mean', 'area')

