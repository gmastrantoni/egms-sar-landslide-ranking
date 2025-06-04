#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 15:31:28 2024

@author: Giandomenico Mastrantoni: giandomenico.mastrantoni@uniroma1.it
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from matplotlib.patches import Patch
import os

os.chdir("/Users/giandomenico/Documents/SAPIENZA/AR/regione_lazio")


# read data
df = pd.read_excel("dati/pluvio/pluvio_20152022_s.elia.xlsx", sheet_name='Cumulate 2_5_10_gg')

# rainfall
rainfall = df.loc[:, ['Data rilevazione', 'Valore', '2gg', '5gg', '7gg', '10gg']]
rainfall['Date'] = pd.to_datetime(rainfall['Data rilevazione'])

# Calculate cumulative sum of 10gg rainfall
rainfall['10gg_cumulative'] = rainfall['10gg'].cumsum()


# Calculate 2-sigma threshold for rainfall
mean_rainfall = rainfall['10gg'].mean()
std_rainfall = rainfall['10gg'].std()

# compute threshold
threshold2 = mean_rainfall + 2*std_rainfall
# Find rainfall peaks (using 90th percentile as threshold)
threshold = np.percentile(rainfall['10gg'].dropna(), 90)
# select peaks based on threshold value
peaks2 = rainfall[rainfall['10gg'] >= threshold2]
peaks = rainfall[rainfall['10gg'] >= threshold]

# save to csv
# rainfall.to_csv("dati/pluvio/rainfall.csv")

# displacement
displ = df.loc[:, ['Data', 'PM46', 'PM6', 'PM110']]
displ['Date'] = pd.to_datetime(displ['Data'])

# # Calculate velocity (over 1-month windows)
# displ = displ.sort_values('Date')
# displ['velocity'] = (displ['PM46'].diff(periods=30) / 30)  # mm/day

# # Calculate acceleration (rate of change of velocity)
# displ['acceleration'] = displ['velocity'].diff()

# # For acceleration
# mean_acc = displ['acceleration'].mean()
# std_acc = displ['acceleration'].std()
# acc_threshold = mean_acc + 2*std_acc

# # Find peaks
# acc_peaks = displ[abs(displ['acceleration']) >= acc_threshold]



# save to csv
# displ.to_csv("dati/pluvio/displacement.csv")


#######################################################################
# Create figure and axis with twin y-axis
plt.rcParams['font.sans-serif'] = "Arial"


fig, ax1 = plt.subplots(figsize=(15, 8))
ax2 = ax1.twinx()

# Plot histogram for 2gg rainfall
VAR = '10gg'

PEAKS = peaks2

for peak_date in PEAKS['Date']:
    ax1.axvspan(peak_date - pd.Timedelta(days=1), 
                peak_date + pd.Timedelta(days=1), 
                alpha=0.1, color='grey')
    # ax2.axvspan(peak_date - pd.Timedelta(days=1), 
    #             peak_date + pd.Timedelta(days=1), 
    #             alpha=0.1, color='grey')
    
    
ax1.bar(rainfall['Date'], rainfall[VAR], 
        alpha=0.7, color='blue', width=pd.Timedelta(days=2),
        label='10-day Rainfall')

# Plot line with dots for PM46 displacement
ax2.plot(displ['Date'], displ['PM46'], 
          'k-', linewidth=1, label='PM46 Displacement')  # Line
ax2.plot(displ['Date'], displ['PM46'], 
          'ko', markersize=3)  # Dots at data points


# Customize the plot
ax1.set_xlabel('Date')
ax1.set_ylabel('10-day Rainfall (mm)', color='blue', fontsize=12)
ax2.set_ylabel('PM46 Displacement (mm)', color='k', fontsize=12)

# Set y-axis limits for displacement
ax2.set_ylim(-80, 80)

# Set tick colors
ax1.tick_params(axis='y', labelcolor='blue')
ax2.tick_params(axis='y', labelcolor='k')


# Format date on x-axis
ax1.xaxis.set_major_formatter(DateFormatter('%Y-%m'))
plt.xticks(rotation=0)

# Add legends
# Create a custom legend for the strips
legend_elements = [Patch(facecolor='grey', alpha=0.2, label=f'Rainfall Peak (2σ = {threshold2:.1f} mm)'),
                  # Patch(facecolor='orange', alpha=0.2, label='Acceleration Peak')
                  ]

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
# ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=14)
ax1.legend(handles=[*ax1.get_legend_handles_labels()[0], *ax2.get_legend_handles_labels()[0], *legend_elements], loc='upper left')

# Add grid
ax1.grid(True, alpha=0.3)

# Add title
plt.title('Rainfall and Displacement Time Series (2015-2021)')

# Adjust layout to prevent label cutoff
plt.tight_layout()

plt.savefig("rainfall_displ_time_series_v1.svg", dpi=500, bbox_inches='tight', facecolor='white', edgecolor='none')





######################################################
# Create figure and subplots
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12), sharex=True)

# Plot rainfall data in top subplot
ax1.bar(rainfall['Date'], rainfall['10gg'], 
        alpha=1, color='blue', width=pd.Timedelta(days=2),
        label='10-day Rainfall')

# Plot displacement data in bottom subplot
ax2.plot(displ['Date'], displ['PM46'], 
          'r-', linewidth=1.5, label='PM46 Displacement')
ax2.plot(displ['Date'], displ['PM46'], 
          'ro', markersize=3)

# Add colored strips for rainfall peaks
ymin1, ymax1 = ax1.get_ylim()
ymin2, ymax2 = -80, 80  # Set displacement y-limits

PEAKS = peaks2

for peak_date in PEAKS['Date']:
    ax1.axvspan(peak_date - pd.Timedelta(days=1), 
                peak_date + pd.Timedelta(days=1), 
                alpha=0.1, color='grey')
    ax2.axvspan(peak_date - pd.Timedelta(days=1), 
                peak_date + pd.Timedelta(days=1), 
                alpha=0.1, color='grey')


# Customize the plots
ax2.set_xlabel('Date')
ax1.set_ylabel('10-day Rainfall (mm)')
ax2.set_ylabel('PM46 Displacement (mm)')

# Set displacement y-limits
ax2.set_ylim(ymin2, ymax2)

# Format date on x-axis
ax2.xaxis.set_major_formatter(DateFormatter('%Y-%m'))
plt.xticks(rotation=0)

# Add grid
ax1.grid(True, alpha=0.3)
ax2.grid(True, alpha=0.3)

# Create a custom legend for the strips
legend_elements = [Patch(facecolor='grey', alpha=0.2, label=f'Rainfall Peak (2σ = {threshold2:.1f} mm)'),
                  # Patch(facecolor='orange', alpha=0.2, label='Acceleration Peak')
                  ]

# Add legends
ax1.legend(handles=[*ax1.get_legend_handles_labels()[0], *legend_elements], loc='upper left')
ax2.legend(handles=[*ax2.get_legend_handles_labels()[0], *legend_elements], loc='upper left')

# Add title
fig.suptitle('Rainfall and Displacement Time Series (2015-2021)', y=.97)

# Adjust layout to prevent label cutoff
plt.tight_layout()


plt.savefig("rainfall_displ_time_series_v2.svg", dpi=500, bbox_inches='tight', facecolor='white', edgecolor='none')


















