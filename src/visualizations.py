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

# -------- LINE CREATION --------
def create_line(p1_id, p2_id, gdf_stops):
    p1 = gdf_stops.loc[
        gdf_stops["cell_id"] == p1_id, "geometry"
    ].iloc[0]

    p2 = gdf_stops.loc[
        gdf_stops["cell_id"] == p2_id, "geometry"
    ].iloc[0]

    return LineString([p1, p2])


# -------- BUILD EDGES --------
def build_edges_gdf(solution_routes_dict, gdf_stops):
    records = []

    for route_id, route in solution_routes_dict.items():
        if not isinstance(route, (list, tuple)):
            continue

        if len(route) < 2:
            continue

        for k in range(len(route) - 1):
            p1 = route[k]
            p2 = route[k + 1]

            line = create_line(p1, p2, gdf_stops)

            records.append({
                "geometry": line,
                "route_id": route_id
            })

    return gpd.GeoDataFrame(records, geometry="geometry", crs=gdf_stops.crs)