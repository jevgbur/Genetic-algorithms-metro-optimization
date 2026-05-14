from pathlib import Path
import zipfile
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as cx
import random
from shapely.geometry import LineString, Polygon, Point, MultiPolygon
import numpy as np
import networkx as nx
from itertools import combinations
import osmnx as ox
import tobler
from collections import defaultdict
import pickle


def generate_trip_weight(df, rangestart, rangestop):
    '''
    This function generates random weights for trips between pairs of nodes in the given dataframe. 
    '''
    # Set a seed so we dont need to save the file locally
    random.seed(154)

    all_nodes = df["cell_id"].tolist()

    pairs = list(combinations(all_nodes, 2))

    o_list = []
    d_list = []
    weights_list = []
    o_p_list = []
    d_p_list = []

    for nodes in pairs:
        ## find the values from the created pairs
        w = random.randrange(rangestart, rangestop)
        o = nodes[0]
        d = nodes[1]

        o_row = df.loc[df['cell_id'].eq(o)]
        d_row = df.loc[df['cell_id'].eq(d)]

        o_point = o_row["geometry"].iloc[0] 
        d_point = d_row["geometry"].iloc[0] 
        
        ## Appending to their list for later population
        o_list.append(o)
        d_list.append(d)
        weights_list.append(w)
        o_p_list.append(o_point)
        d_p_list.append(d_point)


    pair_df = pd.DataFrame({
            "o": o_list,
            "d": d_list,
            "weight": weights_list,
            "o-point": o_p_list,
            "d-point": d_p_list
        })
    
    return pair_df

def generate_trip_weight_V2(df, population_col="weight", seed=154):
    '''
    This function generates random weights for trips between pairs of nodes in the given dataframe. 
    The weight is a random integer between 0 and the sum of the population of the origin and destination nodes. 
    This allows for a more realistic distribution of trip weights, as it takes into account the population of 
    the areas represented by the nodes.
    '''

    # Set a seed so results are reproducible
    random.seed(seed)

    all_nodes = df["cell_id"].tolist()
    pairs = list(combinations(all_nodes, 2))

    o_list = []
    d_list = []
    weights_list = []
    o_p_list = []
    d_p_list = []

    for nodes in pairs:
        o = nodes[0]
        d = nodes[1]

        o_row = df.loc[df["cell_id"].eq(o)]
        d_row = df.loc[df["cell_id"].eq(d)]

        o_point = o_row["geometry"].iloc[0]
        d_point = d_row["geometry"].iloc[0]

        pop_o = o_row[population_col].iloc[0]
        pop_d = d_row[population_col].iloc[0]

        max_w = int(pop_o + pop_d)

        # Random weight between 0 and sum of origin+destination population
        if max_w <= 0:
            w = 0
        else:
            w = random.randint(0, max_w)

        o_list.append(o)
        d_list.append(d)
        weights_list.append(w)
        o_p_list.append(o_point)
        d_p_list.append(d_point)

    pair_df = pd.DataFrame({
        "o": o_list,
        "d": d_list,
        "weight": weights_list,
        "o-point": o_p_list,
        "d-point": d_p_list
    })

    return pair_df

def create_weights(df, od_df):
    '''
    This function creates a new dataframe with weights for each node based on the trip weights between pairs of nodes.
    '''
    weighted_df = df.copy()
    weighted_df["weight"] = ""

    all_nodes = df["cell_id"].tolist()
    
    for unique_node in all_nodes:
        total_weight = 0
        total_weight = od_df.loc[
                (od_df["o"] == unique_node) | (od_df["d"] == unique_node),
                "weight"
            ].sum() 

        weighted_df.loc[weighted_df["cell_id"] == unique_node, 'weight'] = total_weight

        #weighted_df.to_csv("Hexagon_weighted_data.csv", index=False)

    return weighted_df

def finding_neighbors(pointes_weighted, grid):
    '''
    This function finds the neighboring hexagons for each hexagon in the grid and adds this information to the grid dataframe.
    '''
    weighted_grid = grid.copy()

    weighted_grid = weighted_grid.merge(
    pointes_weighted[['cell_id', 'weight']], on='cell_id', how='left')

    mytree = weighted_grid.sindex
    weighted_grid["vicinity"] = weighted_grid.apply(
        lambda x: weighted_grid.iloc[
            mytree.query(x.geometry, predicate="touches")
        ]["cell_id"].tolist(),
        axis=1
    )

    return weighted_grid

def remove_tiny_islands(geom, min_area):
    """
    Keep all polygons larger than min_area.
    Area is in CRS units squared, so use projected CRS in meters.
    Example: 200000 = 0.2 sq km if CRS is meters.
    """
    if geom.geom_type != "MultiPolygon":
        return geom

    kept = [part for part in geom.geoms if part.area >= min_area]

    if not kept:
        return geom
    if len(kept) == 1:
        return kept[0]
    return MultiPolygon(kept)

## Create_grid_1
def Create_grid_1(res, prompt_1, proj_crs, prompt_2=False, prompt_3=False, return_points=False):
    '''
    This function creates a grid of hexagons based on the provided prompts and resolution.
    '''
    # Start with prompt_1
    prompt_1_gdf = ox.geocode_to_gdf(prompt_1)
    merged_geom = prompt_1_gdf.union_all()

    # Add prompt_2 if provided
    if prompt_2:
        prompt_2_gdf = ox.geocode_to_gdf(prompt_2)
        merged_geom = merged_geom.union(prompt_2_gdf.union_all())

    # Add prompt_3 if provided
    if prompt_3:
        prompt_3_gdf = ox.geocode_to_gdf(prompt_3)
        merged_geom = merged_geom.union(prompt_3_gdf.union_all())

    # Back into GeoDataFrame and project
    merged = gpd.GeoDataFrame(
        {"name": ["merged_area"]},
        geometry=[merged_geom],
        crs=prompt_1_gdf.crs
    ).to_crs(proj_crs)

    # Use projected geometry from here
    geom = merged.geometry.iloc[0]

    # Keep only the largest area
    if isinstance(geom, MultiPolygon):
        geom = remove_tiny_islands(geom, min_area=20000000)

    my_polygon = gpd.GeoDataFrame(
        {"name": ["merged_area"]},
        geometry=[geom],
        crs=proj_crs
    )

    # make bbox
    coords = my_polygon.get_coordinates()
    xmin = min(coords.x)
    xmax = max(coords.x)
    ymin = min(coords.y)
    ymax = max(coords.y)

    bbox = Polygon([
        Point([xmin, ymin]),
        Point([xmax, ymin]),
        Point([xmax, ymax]),
        Point([xmin, ymax])
    ])

    bbox = gpd.GeoDataFrame({"geometry": [bbox]}, crs=my_polygon.crs)

    # make grid
    grid = tobler.util.h3fy(
        source=bbox,
        resolution=res,
        clip=False,
        buffer=False,
        return_geoms=True
    )

    grid["hex_id"] = grid.index
    grid = grid.reset_index(drop=True)
    grid["cell_id"] = grid.index
    grid = grid.to_crs(proj_crs)

    poly = my_polygon.union_all()

    # centroid of each hexagon
    grid["centroid"] = grid.geometry.centroid

    # True/False: centroid lies inside polygon
    grid["centroid_inside"] = grid["centroid"].within(poly)

    # keep only hexagons whose centroid is inside
    grid_inside = grid[grid["centroid_inside"]].copy()

    # representative points
    points = grid_inside.copy()
    points["geometry"] = points.representative_point()

    if return_points:
        return grid_inside, points, my_polygon
    else:
        return grid_inside

def clean_postal_codes(path):
    '''
    This function reads a CSV file containing postal codes and population data, cleans the data, and returns a DataFrame with postal codes and their corresponding populations. 
    It ensures that postal codes are in the correct format (4 digits) and that population values are numeric. 
    The function also handles any missing or malformed data by dropping rows with invalid postal codes or population values.
    The resulting DataFrame can be used for further analysis or integration with other datasets.
    '''
    file_path = Path(path)
    rows = []

    with open(file_path, "r", encoding="latin1") as f:
        next(f)  

        for line in f:
            parts = [p.strip().strip('"') for p in line.split(",")]

            if len(parts) >= 4:
                postcode_text = parts[2]
                population_text = parts[-1] 
                if postcode_text[:4].isdigit():
                    rows.append({
                        "postal_code": postcode_text[:4],
                        "population": population_text
                    })

    pop_df = pd.DataFrame(rows)

    pop_df["postal_code"] = pop_df["postal_code"].astype(str).str.zfill(4)
    pop_df["population"] = pd.to_numeric(pop_df["population"], errors="coerce")

    pop_df = pop_df.dropna(subset=["postal_code", "population"])

    return pop_df