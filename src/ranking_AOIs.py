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
DC_ASC_PATH = "dati/RESULTS_EGMS_BASIC_MODEL/ASC/DATACLUSTER_ASC_RESIZED.shp"
DC_DESC_PATH = "dati/RESULTS_EGMS_BASIC_MODEL/DESC/DATACLUSTER_DESC_RESIZED.shp"
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
    "geometry"
    ]

dc_asc = gpd.read_file(DC_ASC_PATH).loc[:,cols_to_keep] # datacluster ASC orbit
dc_desc = gpd.read_file(DC_DESC_PATH).loc[:,cols_to_keep] # datacluster DESC orbit

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
def dc_intersect(dc_asc, dc_desc):
    #drop duplicated ID
    dc_asc.drop_duplicates(subset = "CLUSTER_ID")
    dc_desc.drop_duplicates(subset = "CLUSTER_ID")
    #check CRS
    if dc_asc.crs != dc_desc.crs:
        dc_asc = dc_asc.to_crs(dc_desc.crs)
    
    # Binary Intersects
    # # Create a unary union of all geometries in dc_desc
    dc_desc_union = dc_desc.unary_union
    dc_asc_union = dc_asc.unary_union
    # # Use intersects with the unary union
    dc_asc['int_orb'] = dc_asc.geometry.apply(lambda geom: geom.intersects(dc_desc_union))
    dc_desc['int_orb'] = dc_desc.geometry.apply(lambda geom: geom.intersects(dc_asc_union))
    
    
    # spatial join with comuni
    dc_asc = gpd.sjoin(dc_asc, comuni_asc, how='left', predicate='intersects').drop(columns='index_right')
    dc_desc = gpd.sjoin(dc_desc, comuni_desc, how='left', predicate='intersects').drop(columns='index_right')
    # add column with orbit type info
    dc_asc['orbit'] = 'ASC'
    dc_desc['orbit'] = 'DESC'
    return dc_asc, dc_desc


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

# Define the function to  compute Score_Area
def score_AREA(v):
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
        
def score_VEL(v):
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

def score_frana(v):
    if v == 0:
        return 10
    elif v == 1:
        return 90
    else: print('No match')
    
def score_orbite(v):
    if v == 0:
        return 1
    elif v == 1:
        return 9
    else: print('No match')

def score_loc(v):
    if v == 0:
        return 0.1
    elif v == 1:
        return 0.9
    else: print('No match')

def score_road(v):
    if v == 0:
        return 0.01
    elif v == 1:
        return 0.09
    else: print('No match')

def score_railwa(v):
    if v == 0:
        return 0.001
    elif v == 1:
        return 0.009
    else: print('No match')


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

    # List the columns to be summed
    columns_to_sum = ['score_AREA', 'score_VEL', 'score_fra',
                      "score_orb", "score_loc", "score_road", "score_rail"]
    dc['score_TOT'] = dc[columns_to_sum].sum(axis=1).round(3)
    
    return dc


def calculate_score_prodotto(df_area, df_vel):
    df_area_copy = df_area.copy()

    score_area = df_area_copy['score_TOT']
    score_vel = df_vel['score_TOT']
    df_area_copy.rename(columns={'score_TOT': 'tot_area'}, inplace=True)
    df_area_copy['tot_vel'] = score_vel
    
    df_area_copy['score_prod'] = 0.0
    df_area_copy['score_prod'] = (score_area*score_vel / 1000).round(3)
    return df_area_copy


#----------------------PROCESSING----------------------#
# Calculate intersection between AOIs ASC DES
dc_asc, dc_desc = dc_intersect(dc_asc, dc_desc)

# Calculate intersection % with PAI polygons
# Create a new column 'overlap_percentage' in dc_asc and initialize it with 0
dc_asc['pai_overl'] = 0.0
dc_desc['pai_overl'] = 0.0
# Apply the function to each geometry in dc_asc
dc_asc['pai_overl'] = dc_asc.geometry.apply(lambda geom: aoi_pai_overlap(geom, pai, pai_index))
dc_desc['pai_overl'] = dc_desc.geometry.apply(lambda geom: aoi_pai_overlap(geom, pai, pai_index))

# Calculate SCORES
RANKING_COL = "AREA"
dc_asc_AREA = calculate_scores(dc_asc, RANKING_COL)
dc_desc_AREA = calculate_scores(dc_desc, RANKING_COL)

RANKING_COL = "VEL"
dc_asc_VEL = calculate_scores(dc_asc, RANKING_COL)
dc_desc_VEL = calculate_scores(dc_desc, RANKING_COL)


# Calculate Score PRODOTTO
dc_asc_prod = calculate_score_prodotto(dc_asc_AREA, dc_asc_VEL)
dc_desc_prod = calculate_score_prodotto(dc_desc_AREA, dc_desc_VEL)



#----------------------SAVE DATA----------------------#
if not os.path.exists('Results'):
    os.makedirs('Results')
    
dc_asc_prod.to_file(os.path.join(CWD, 'Results/AOIs_ASC_Ranking.shp')) #save shapefile of ASC AOIs in results folder
dc_desc_prod.to_file(os.path.join(CWD, 'Results/AOIs_DESC_Ranking.shp')) #save shapefile of DESC AOIs in results folder



