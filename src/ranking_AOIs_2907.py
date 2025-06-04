#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 31 11:56:13 2024

@author: Giandomenico Mastrantoni: giandomenico.mastrantoni@uniroma1.it
"""

#----------------------IMPORT----------------------#
import pandas as pd
import geopandas as gpd
import numpy as np
import os
from shapely.geometry import Polygon
from rtree import index


#----------------------SET MAIN DIRECTORY----------------------#
CWD = "/Users/giandomenico/Documents/SAPIENZA/AR/regione_lazio" # change based on your main directory

os.chdir(CWD)

#----------------------SET FILEPATHS----------------------#
# modify according to your filepaths
DC_ASC_PATH = "debug/test_data/DATACLUSTER_ASC_2015_2021_parte_per_test.shp"
DC_DESC_PATH = "debug/test_data/DATACLUSTER_DESC_2015_2021_parte_per_test.shp"
AOI_ASC_PATH = "debug/test_data/AOI_ASC_2015_2021_parte_per_test.shp"
AOI_DESC_PATH = "debug/test_data/AOI_DESC_2015_2021_parte_per_test.shp"

PAI_PATH = "dati/PAI/PAI_ISPRA_LATINA.shp"
COMUNI_ASC_PATH = "dati/RESULTS_EGMS_BASIC_MODEL/ASC/AOI_ASC_punteggio_comuni_POST_VALIDATION.shp"
COMUNI_DESC_PATH = "dati/RESULTS_EGMS_BASIC_MODEL/DESC/AOI_DESC_punteggio_comuni_POST_VALIDATION.shp"


#----------------------INPUT DATA----------------------#
cols_to_keep = [	
    "CLUSTER_ID",
    "vel_median", "vel_min", "vel_max",
    "j_median", "j_min", "j_max",
    "Area_AOI", "perimeter",
    "iffi_inter", "pai_inters", "loc_inters", "int_railwa", "road_inter",
    # "geometry"
    ]

dc_asc = gpd.read_file(DC_ASC_PATH).loc[:,cols_to_keep] # datacluster ASC orbit
dc_desc = gpd.read_file(DC_DESC_PATH).loc[:,cols_to_keep] # datacluster DESC orbit
aoi_asc = gpd.read_file(AOI_ASC_PATH) # AOIs ASC ORBIT
aoi_desc = gpd.read_file(AOI_DESC_PATH) # AOIs DESC ORBIT
pai = gpd.read_file(PAI_PATH) # PAI landslides polygons
# Build a spatial index for the PAI polygons
pai_index = index.Index()
for i, geom in enumerate(pai.geometry):
    pai_index.insert(i, geom.bounds)

#Comuni
comuni_asc = gpd.read_file(COMUNI_ASC_PATH).loc[:,['COMUNE','geometry']]
comuni_desc = gpd.read_file(COMUNI_DESC_PATH).loc[:,['COMUNE','geometry']]


#----------------------FUNCTIONS DEF----------------------#
# cleaning and AOIs intersection
def aoi_dc_intersect(dc_asc, dc_desc, aoi_asc, aoi_desc):
    #drop duplicated ID
    dc_asc = dc_asc.drop_duplicates(subset = "CLUSTER_ID")
    dc_desc = dc_desc.drop_duplicates(subset = "CLUSTER_ID")
    #check CRS
    if aoi_asc.crs != aoi_desc.crs:
        aoi_asc = aoi_asc.to_crs(aoi_desc.crs)
    
    # Binary Intersects
    # # Create a unary union of all geometries in dc_desc
    aoi_asc_union = aoi_asc.unary_union
    aoi_desc_union = aoi_desc.unary_union
    # # Use intersects with the unary union
    aoi_asc['int_orb'] = aoi_asc.geometry.apply(lambda geom: geom.intersects(aoi_desc_union))
    aoi_desc['int_orb'] = aoi_desc.geometry.apply(lambda geom: geom.intersects(aoi_asc_union))
    
    # Merging aoi - dc
    aoi_asc = pd.merge(aoi_asc, dc_asc, on='CLUSTER_ID')
    aoi_desc = pd.merge(aoi_desc, dc_desc, on='CLUSTER_ID')

    # spatial join with comuni
    aoi_asc = gpd.sjoin(aoi_asc, comuni_asc, how='left', predicate='intersects').drop(columns='index_right')
    aoi_desc = gpd.sjoin(aoi_desc, comuni_desc, how='left', predicate='intersects').drop(columns='index_right')
    # add column with orbit type info
    aoi_asc['orbit'] = 'ASC'
    aoi_desc['orbit'] = 'DESC'
    return dc_asc, dc_desc, aoi_asc, aoi_desc


def aoi_pai_overlap(geom, pai, pai_index):
    # Find potential intersections using the spatial index
    potential_intersections = [pai.geometry[i] for i in pai_index.intersection(geom.bounds)]
    if not potential_intersections:
        return 0.0
    # Calculate the intersection with the potential landslide polygons
    intersection = geom.intersection(gpd.GeoSeries(potential_intersections).unary_union)
    # Check if the intersection is empty
    if intersection.is_empty:
        return 0.0
    # Calculate the area of the intersection
    intersection_area = intersection.area if intersection is not None else 0.0
    # Calculate the area of the original geometry
    original_area = geom.area
    # Calculate the percentage of overlap
    overlap_percentage = (intersection_area / original_area) * 100 if original_area > 0 else 0
    
    return overlap_percentage

# Define the functions to compute the Scores.
def score_AREA(v):
    if RANKING_TYPE == 'Area-Vel':
        if RANKING_COL == 'AREA':
            if v <= 0.0025:
                return 1000
            elif v <= 0.005:
                return 2000
            elif v <= 0.0075:
                return 3000
            elif v <= 0.01:
                return 4000
            elif v <= 0.0125:
                return 5000
            elif v <= 0.015:
                return 6000
            else:  # v > 0.015
                return 7000
        else:
            if v <= 0.0025:
                return 100
            elif v <= 0.005:
                return 200
            elif v <= 0.0075:
                return 300
            elif v <= 0.01:
                return 400
            elif v <= 0.0125:
                return 500
            elif v <= 0.015:
                return 600
            else:  # v > 0.015
                return 700
    else:                           # RANKING_TYPE = 'Loc-Inf'
        if v <= 0.0025:
            return 1
        elif v <= 0.005:
            return 2
        elif v <= 0.0075:
            return 3
        elif v <= 0.01:
            return 4
        elif v <= 0.0125:
            return 5
        elif v <= 0.015:
            return 6
        else:  # v > 0.015
            return 7
        
def score_VEL(v):
    if RANKING_TYPE == 'Area-Vel':
        if RANKING_COL == 'VEL':
            if v <= 3:
                return 1000
            elif v <= 4:
                return 2000
            elif v <= 5:
                return 3000
            elif v <= 6:
                return 4000
            elif v <= 7:
                return 5000
            elif v <= 8:
                return 6000
            elif v <= 9:
                return 7000
            else:  # v > 9
                return 8000
        else:
            if v <= 3:
                return 100
            elif v <= 4:
                return 200
            elif v <= 5:
                return 300
            elif v <= 6:
                return 400
            elif v <= 7:
                return 500
            elif v <= 8:
                return 600
            elif v <= 9:
                return 700
            else:  # v > 9
                return 800
    else:                       # RANKING_TYPE = 'Loc-Inf'
        if v <= 3:
            return 10
        elif v <= 4:
            return 20
        elif v <= 5:
            return 30
        elif v <= 6:
            return 40
        elif v <= 7:
            return 50
        elif v <= 8:
            return 60
        elif v <= 9:
            return 70
        else:  # v > 9
            return 80
        

def score_frana(v):
    if RANKING_TYPE == 'Area-Vel':
        if v == 0:
            return 10
        elif v == 1:
            return 90
        else: print('No match')
    else:                       # RANKING_TYPE = 'Loc-Inf'
        if v == 0:
            return 0.1
        elif v == 1:
            return 0.9
        else: print('No match')
        
    
def score_orbite(v):
    if RANKING_TYPE == 'Area-Vel':
        if v == 0:
            return 1
        elif v == 1:
            return 9
        else: print('No match')
    else:                       # RANKING_TYPE = 'Loc-Inf'
        if v == 0:
            return 0.01
        elif v == 1:
            return 0.09
        else: print('No match')
        

def score_loc(v):
    if RANKING_TYPE == 'Area-Vel':
        if v == 0:
            return 0.1
        elif v == 1:
            return 0.9
        else: print('No match')
    else:                       # RANKING_TYPE = 'Loc-Inf'
        if RANKING_COL == 'LOC':
            if v == 0:
                return 1000
            elif v == 1:
                return 2000
            else: print('No match')
        else:
            if v == 0:
                return 100
            elif v == 1:
                return 200
            else: print('No match')

def score_road(v):
    if RANKING_TYPE == 'Area-Vel':
        if v == 0:
            return 0.01
        elif v == 1:
            return 0.09
        else: print('No match')
    else:
        pass

def score_railwa(v):
    if RANKING_TYPE == 'Area-Vel':
        if v == 0:
            return 0.001
        elif v == 1:
            return 0.009
        else: print('No match')
    else:
        pass

def score_infrastrutture(v): # Road + Infr
    if RANKING_TYPE == 'Loc-Inf':
        if RANKING_COL == 'LOC':
            if v == 0:
                return 100
            elif v == 1:
                return 200
            elif v == 2:
                return 200
            else: print('No match')
        else:
            if v == 0:
                return 1000
            elif v == 1:
                return 2000
            elif v == 2:
                return 2000
            else: print('No match')
    else:                       # RANKING_TYPE != 'Loc-Inf'
        pass


def calculate_scores(df, RANKING_COL):
    # make a copy of geodataframe
    dc = df.copy()
    
    dc['max_min'] = dc[['j_min', 'j_max']].abs().max(axis=1)
    dc['score_AREA'] = dc['Area_AOI'].apply(score_AREA)
    dc['score_VEL'] = dc['max_min'].apply(score_VEL)
    dc['score_fra'] = dc['pai_inters'].apply(score_frana)
    dc['score_orb'] = dc['int_orb'].apply(score_orbite)
    dc['score_loc'] = dc['loc_inters'].apply(score_loc)
    dc['score_road'] = dc['road_inter'].apply(score_road)
    dc['score_rail'] = dc['int_railwa'].apply(score_railwa)
    dc['score_infras'] = (dc['road_inter']+dc['int_railwa']).apply(score_infrastrutture)
    
    if RANKING_TYPE == 'Area-Vel':    
        # List the columns to be summed
        columns_to_sum = ['score_AREA', 'score_VEL', 'score_fra',
                          "score_orb", "score_loc", "score_road",
                          "score_rail"]
        if RANKING_COL == 'AREA':
            dc['score_TOT_A'] = dc[columns_to_sum].sum(axis=1).round(3)
        else:
            dc['score_TOT_V'] = dc[columns_to_sum].sum(axis=1).round(3)
        return dc
    else:
        # List the columns to be summed
        columns_to_sum = ['score_AREA', 'score_VEL', 'score_fra',
                          "score_orb", "score_loc", "score_infras"]
        if RANKING_COL == 'LOC':
            dc['score_TOT_L'] = dc[columns_to_sum].sum(axis=1).round(3)
        else:
            dc['score_TOT_I'] = dc[columns_to_sum].sum(axis=1).round(3)            
        return dc


def calculate_score_prodotto(df1, df2):
    df1_copy = df1.copy()
    if RANKING_TYPE == 'Area-Vel':
        score_area = df1_copy['score_TOT_A']
        score_vel = df2['score_TOT_V']
        df1_copy.rename(columns={'score_TOT_A': 'tot_area'}, inplace=True)
        df1_copy['tot_vel'] = score_vel
        
        df1_copy['score_prod_A-V'] = 0.0
        df1_copy['score_prod_A-V'] = (score_area*score_vel / 1000).round(3)
        return df1_copy
    else:
        score_loc = df1_copy['score_TOT_L']
        score_inf = df2['score_TOT_I']
        df1_copy.rename(columns={'score_TOT_L': 'tot_loc'}, inplace=True)
        df1_copy['tot_inf'] = score_inf
        
        df1_copy['score_prod_L-I'] = 0.0
        df1_copy['score_prod_L-I'] = (score_loc*score_inf / 1000).round(3)
        return df1_copy


#----------------------PROCESSING----------------------#
# Calculate intersection between AOIs ASC DES
dc_asc, dc_desc, aoi_asc, aoi_desc = aoi_dc_intersect(dc_asc, dc_desc, aoi_asc, aoi_desc)

# Calculate intersection % with PAI polygons
# Create a new column 'overlap_percentage' in dc_asc and initialize it with 0
aoi_asc['pai_overl'] = 0.0
aoi_desc['pai_overl'] = 0.0
# Apply the function to each geometry in dc_asc
aoi_asc['pai_overl'] = aoi_asc.geometry.apply(lambda geom: aoi_pai_overlap(geom, pai, pai_index))
aoi_desc['pai_overl'] = aoi_desc.geometry.apply(lambda geom: aoi_pai_overlap(geom, pai, pai_index))

# Calculate SCORES
RANKING_TYPE = 'Area-Vel'
RANKING_COL = "AREA"
aoi_asc_AREA = calculate_scores(aoi_asc, RANKING_COL)
aoi_desc_AREA = calculate_scores(aoi_desc, RANKING_COL)
RANKING_COL = "VEL"
aoi_asc_VEL = calculate_scores(aoi_asc, RANKING_COL)
aoi_desc_VEL = calculate_scores(aoi_desc, RANKING_COL)
# Calculate Score PRODOTTO
aoi_asc_prod_AV = calculate_score_prodotto(aoi_asc_AREA, aoi_asc_VEL)
aoi_desc_prod_AV = calculate_score_prodotto(aoi_desc_AREA, aoi_desc_VEL)


#----LOC _ INF ------#
RANKING_TYPE = 'Loc-Inf'
RANKING_COL = "LOC"
aoi_asc_LOC = calculate_scores(aoi_asc, RANKING_COL)
aoi_desc_LOC = calculate_scores(aoi_desc, RANKING_COL)

RANKING_COL = "INF"
aoi_asc_INF = calculate_scores(aoi_asc, RANKING_COL)
aoi_desc_INF = calculate_scores(aoi_desc, RANKING_COL)

# Calculate Score PRODOTTO
aoi_asc_prod_LI = calculate_score_prodotto(aoi_asc_LOC, aoi_asc_INF)
aoi_desc_prod_LI = calculate_score_prodotto(aoi_desc_LOC, aoi_desc_INF)

# Combine into unique df per orbit
aoi_asc_ranking = pd.merge(aoi_asc_prod_AV, aoi_asc_prod_LI[['CLUSTER_ID','score_prod_L-I']], on='CLUSTER_ID')
aoi_desc_ranking = pd.merge(aoi_desc_prod_AV, aoi_desc_prod_LI[['CLUSTER_ID','score_prod_L-I']], on='CLUSTER_ID')


#----------------------SAVE DATA----------------------#
if not os.path.exists('Results'):
    os.makedirs('Results')

cols_to_keep = ['CLUSTER_ID', 'COD_PROV', 'COMUNE_left', 'PROVINCIA', 'orbita',
                'score_prod_A-V', 'score_prod_L-I', 'geometry']
aoi_asc_ranking[cols_to_keep].to_file(os.path.join(CWD, 'Results/AOIs_ASC_Ranking.gpkg'), driver='GPKG') #save shapefile of ASC AOIs in results folder
aoi_desc_ranking[cols_to_keep].to_file(os.path.join(CWD, 'Results/AOIs_DESC_Ranking.gpkg'), driver='GPKG') #save shapefile of DESC AOIs in results folder

print(f'Analisi Completata! \nRisultati salvati in "{CWD}/Results"')

