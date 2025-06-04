#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 10:48:30 2024

@author: Giandomenico Mastrantoni: giandomenico.mastrantoni@uniroma1.it
"""

import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt

os.chdir("/Users/giandomenico/Documents/SAPIENZA/AR/regione_lazio")

data = pd.read_excel("dati/differenza_VEL_AOIs_intersect.xlsx")


# Set the seaborn theme with improved styling
sns.set_theme(context='paper', style="ticks", font='arial', font_scale=1.5)
sns.set_palette("deep")  # Using a more vibrant color palette

# Create the joint plot with enhanced features
g = sns.jointplot(
    data=data,
    x="VEL_2015_2021",
    y="VEL_2018_22",
    hue="orbita",
    height=7,  # Larger figure size
    ratio=8,    # Adjust the ratio of main plot to marginal plots
    joint_kws={"s": 100, "alpha": 0.7},     # Larger points with some transparency
)

# Customize the plot further
g.fig.suptitle("AOIs EGMS Velocity Comparison", y=.95, fontsize=16)  # Add main title

# Format axis labels
g.ax_joint.set_xlabel("Velocity 2015-2021 mm/y", fontsize=14, fontweight='bold')
g.ax_joint.set_ylabel("Velocity 2018-2022 mm/y", fontsize=14, fontweight='bold')

# Add grid for better readability
g.ax_joint.grid(True, linestyle='--', alpha=0.3)

# Adjust layout to prevent label cutoff
plt.tight_layout()

# Save the plot with high resolution
plt.savefig('AOI_velocity_comparison.png', 
            dpi=330,              # High DPI for quality
            bbox_inches='tight',  # Tight bounding box
            facecolor='white',    # White background
            edgecolor='none')     # No edge color

plt.show()


# # Create the Resid plot with enhanced features
# g = sns.jointplot(
#     data=data,
#     kind='resid',
#     x="VEL_2015_2021",
#     y="VEL_2018_22",
#     # hue="orbita",
#     height=7,  # Larger figure size
#     ratio=8,    # Adjust the ratio of main plot to marginal plots
#     # joint_kws={"s": 100, "alpha": 0.7},     # Larger points with some transparency
# )

# # Customize the plot further
# g.fig.suptitle("AOIs EGMS Residual Velocity Comparison", y=.95, fontsize=16)  # Add main title

# # Format axis labels
# g.ax_joint.set_xlabel("Velocity 2015-2021 mm/y", fontsize=14, fontweight='bold')
# g.ax_joint.set_ylabel("Velocity 2018-2022 mm/y", fontsize=14, fontweight='bold')

# # Add grid for better readability
# g.ax_joint.grid(True, linestyle='--', alpha=0.3)

# # Adjust layout to prevent label cutoff
# plt.tight_layout()

# # Save the plot with high resolution
# plt.savefig('AOI_residual_velocity_comparison.png', 
#             dpi=330,              # High DPI for quality
#             bbox_inches='tight',  # Tight bounding box
#             facecolor='white',    # White background
#             edgecolor='none')     # No edge color

# plt.show()


# Calculate residuals
data['residuals'] = data['VEL_2018_22'] - data['VEL_2015_2021']

# Set the seaborn theme with improved styling
sns.set_theme(context='paper', style="ticks", font='arial', font_scale=1.5)
sns.set_palette("deep")  # Using a more vibrant color palette

# Create the joint plot for residuals
g = sns.jointplot(
    data=data,
    x="VEL_2015_2021",
    y="residuals",
    hue="orbita",
    height=7,  # Larger figure size
    ratio=8,    # Adjust the ratio of main plot to marginal plots
    joint_kws={"s": 100, "alpha": 0.7},     # Larger points with some transparency
)

# Add horizontal line at y=0 for reference
g.ax_joint.axhline(y=0, color='black', linestyle='--', alpha=0.5)

# Customize the plot further
g.fig.suptitle("Residual Analysis: 2015-2021 vs 2018-2022", y=.95, fontsize=16)  # Add main title

# Format axis labels
g.ax_joint.set_xlabel("Velocity 2015-2021 (mm/year)", fontsize=14, fontweight='bold')
g.ax_joint.set_ylabel("Residuals (mm/year)", fontsize=14, fontweight='bold')

# Add grid for better readability
g.ax_joint.grid(True, linestyle='--', alpha=0.3)

# Optionally add text with summary statistics
residuals_mean = data['residuals'].mean()
residuals_std = data['residuals'].std()
stats_text = f'Mean: {residuals_mean:.2f}\nStd: {residuals_std:.2f}'
g.ax_joint.text(0.02, 0.98, stats_text,
                transform=g.ax_joint.transAxes,
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

# Adjust layout to prevent label cutoff
plt.tight_layout()

# Save the plot with high resolution
plt.savefig('AOIs_velocity_residuals_hue.png', 
            dpi=330,              # High DPI for quality
            bbox_inches='tight',  # Tight bounding box
            facecolor='white',    # White background
            edgecolor='none')     # No edge color

plt.show()