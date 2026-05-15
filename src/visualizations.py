
import geopandas as gpd
from shapely.geometry import LineString

def create_line(p1_id, p2_id, gdf_stops):
    '''
    This function creates a LineString geometry between two points (p1 and p2) based on their IDs and a GeoDataFrame of stops.
    It retrieves the geometries of the two points from the GeoDataFrame using their IDs and then creates a LineString connecting them.
    The resulting LineString can be used to represent a route or connection between the two stops in a spatial context, such as in a metro or transportation network visualization.
    '''
    p1 = gdf_stops.loc[
        gdf_stops["cell_id"] == p1_id, "geometry"
    ].iloc[0]

    p2 = gdf_stops.loc[
        gdf_stops["cell_id"] == p2_id, "geometry"
    ].iloc[0]

    return LineString([p1, p2])

def metro_edges_gdf(solution_routes_dict, gdf_stops):
    '''
    This function builds a GeoDataFrame of edges representing the routes in the solution.
    It iterates through the routes in the solution, creates LineString geometries for each pair of consecutive stops, and stores them in a GeoDataFrame along with the route ID.
    The resulting GeoDataFrame can be used for visualizing the metro routes on a map or for further spatial analysis.
    '''
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


def build_graph_edges_gdf(G, gdf_stops, node_col="cell_id"):
    '''
    This function builds a GeoDataFrame of edges representing the connections in the graph G.
    It iterates through the edges in the graph, creates LineString geometries for each pair of connected nodes, and stores them in a GeoDataFrame along with the from_node and to_node IDs.
    The resulting GeoDataFrame can be used for visualizing the graph connections on a map or for further spatial analysis.
    '''
    records = []

    valid_nodes = set(gdf_stops[node_col])

    for u, v in G.edges():
        if u not in valid_nodes or v not in valid_nodes:
            continue

        try:
            line = create_line(u, v, gdf_stops)
            records.append({
                "geometry": line,
                "from_node": u,
                "to_node": v
            })
        except IndexError:
            continue

    return gpd.GeoDataFrame(records, geometry="geometry", crs=gdf_stops.crs)


def build_edges_gdf(solution_routes_dict, gdf_stops):
    '''
    This function builds a GeoDataFrame of edges representing the routes in the solution.
    It iterates through the routes in the solution, creates LineString geometries for each pair of consecutive stops, and stores them in a GeoDataFrame along with the route ID.
    The resulting GeoDataFrame can be used for visualizing the metro routes on a map or for further spatial analysis.
    '''
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