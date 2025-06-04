#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 14 17:18:25 2024

@author: Giandomenico Mastrantoni: giandomenico.mastrantoni@uniroma1.it
"""

import geopandas as gpd
import mapclassify
import os
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
CWD = "/Users/giandomenico/Documents/SAPIENZA/AR/regione_lazio" # change based on your main directory

os.chdir(CWD)

#%% SET COLUMN VARIABLES and CLASS BREAK METHOD
# Filepath to the AOI shapefile
AOI_FILEPATH = "dati/AOI_Finali/AOIs_RLAZIO_CONSEGNA_FINALE.shp" # percorso al file di input con le AOI e i due ranking.
# Output filename
OUT_FILENAME = 'ranking_doppio_finale.gpkg' # nome del file in uscita.

# Insert column names for ranking A and ranking B.
INTENSITY_COL = 'RANK PERIC' # scrivere il nome della colonna del ranking area-vel

INTERFERENCE_COL = 'RANK RISCH' # scrivere il nome della colonna del ranking loc_infrastrutture

CLASSIFIER = mapclassify.UserDefined.make(bins=[7421.23, 27132.34, 70000]) # Classificatore per divisione in classi. Può essere modificato.
CLASSIFIER_2 = mapclassify.NaturalBreaks.make(k=3)
# Aggiungi o rimuovi in base alle colonne che vuoi mantenere nel risultato.
COLS_TO_KEEP = ['COMUNE', 'PROVINCIA', 'orbita', 'Area AOI',
                'VEL MAX', 'ID_ORBITA',
                'geometry',
                INTENSITY_COL, INTERFERENCE_COL]

########### NON MODIFICARE NULLA DA QUI IN POI ################

#%% IMPORTING THE DATA AND PROCESSING
data = gpd.read_file(AOI_FILEPATH)

# data['j_prodotto'] = np.random.choice(data['score_prod'], len(data))

# create a copy with a subset of columns
data_classes = data.copy()[COLS_TO_KEEP]

# apply clf
data_classes[INTENSITY_COL+'_c'] = data_classes[[INTENSITY_COL]].apply(CLASSIFIER)
data_classes[INTERFERENCE_COL+'_c'] = data_classes[[INTERFERENCE_COL]].apply(CLASSIFIER_2)

# map values 0-1-2 to basso-medio-alto
map_classes = {0:'basso', 1:'medio', 2:'alto'}
data_classes['CLASSI_PERIC'] = data_classes[INTENSITY_COL+'_c'].map(map_classes)
data_classes['CLASSI_RISCH'] = data_classes[INTERFERENCE_COL+'_c'].map(map_classes)

# drop columns
data_classes = data_classes.drop(columns=[INTENSITY_COL+'_c', INTERFERENCE_COL+'_c'])

# compute the categorical bivariate column
data_classes['CLASSI_BIV'] = data_classes['CLASSI_PERIC'] + '-' + data_classes['CLASSI_RISCH']

print(f'IMPORTANTE:\n Il primo valore della colonna ranking_biv si riferisce a "{INTENSITY_COL}",\n Il secondo valore si riferisci a "{INTERFERENCE_COL}".')


#%% SAVE RESULTS into Results folder.
if not os.path.exists('results'):
    os.makedirs('results')
    
data_classes.to_file(os.path.join(CWD, 'results/{}').format(OUT_FILENAME))

#%% PLOT HIST
col_plot = INTENSITY_COL
hue_col = 'CLASSI_PERIC'
data_classes = data_classes.sort_values(by=[col_plot], ascending = True)

# Create a figure and axis
fig, ax = plt.subplots(figsize=(10, 6), dpi=330)

# Plot the bars
bar_plot = sns.barplot(x=np.arange(0, len(data_classes)), y=col_plot,
                       data=data_classes, palette='Set2', hue=hue_col,
                       ax=ax)

# Set the x-axis tick labels
num_features = len(data_classes)
xtick_values = np.arange(0, num_features, 500)
xtick_labels = ['{:,.0f}'.format(x) for x in xtick_values]
plt.xticks(xtick_values, xtick_labels, rotation=0, fontsize=12)

# Set the title and axis labels
plt.title(f'Bars Ordered by {col_plot} and Colored by {hue_col}', fontsize=14)
plt.xlabel('Feature Number', fontsize=12)
plt.ylabel(f'{col_plot}', fontsize=12)

# Show the legend
plt.legend(bbox_to_anchor=(0.05, 0.95), loc='upper left', borderaxespad=0, fontsize=14)

# Adjust the layout to prevent overlapping labels
plt.tight_layout()

plt.savefig(f'results/barplot_{col_plot}.png', format='PNG', dpi=330)
# Display the plot
plt.show()
