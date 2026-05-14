import pandas as pd
import random
import numpy as np
import networkx as nx
from itertools import combinations

def cal_scoreV2(G, od_df, neighbor_df, pair_weights):  
    demand_graph = G.copy()
    vicinity_lookup = neighbor_df.set_index("cell_id")["vicinity"].to_dict()
    nodes_to_add = set()
    for node in G.nodes():
        nodes_to_add.update(vicinity_lookup.get(node, []))
    demand_graph.add_nodes_from(nodes_to_add)

    temp_score = 0
    pairs = list(combinations(demand_graph.nodes(), 2))
    for (node1, node2) in pairs:
        key = (min(node1, node2), max(node1, node2))
        temp_score += pair_weights.get(key, 0)

    total_demand = od_df["weight"].sum()
    evaluation_score = (temp_score / total_demand) * 100
    
    ######################################### New part 
    
    shortest_paths = dict(nx.shortest_path(G))
    
    total_path_length = 0
    total_pairs = 0
    total_transfers = 0

    for origin in shortest_paths:

        for destination in shortest_paths[origin]:

            if origin == destination:
                continue

            path = shortest_paths[origin][destination]

            path_length = len(path) - 1 # amount of edges traveled, not amount of nodes
            
            transfers = count_transfers(G, path)

            total_path_length += path_length
            total_pairs += 1
            total_transfers += transfers

    average_shortest_path = total_path_length / total_pairs
    average_transfers = total_transfers / total_pairs

    return evaluation_score, average_shortest_path, average_transfers

def select_parents(generation, top_performers, random_performers, sample_size, number_of_parents):
    best_performing = []
    sorted_gen = sorted(generation, key=lambda x: x["Score as %"], reverse=True)
    for i in range(top_performers):
        best_performing.append(sorted_gen[i])

    random_added_parents = 0
    while random_added_parents < int(random_performers):
        random_parent = random.choice(generation)
        if random_parent not in best_performing:
            best_performing.append(random_parent)
            random_added_parents += 1

    while len(best_performing) < int(number_of_parents):
        competitors = random.sample(generation, sample_size)
        best = max(competitors, key=lambda x: x["Score as %"])
        if best not in best_performing:
            best_performing.append(best)
    return best_performing

def TriangleCheck(poss_neighbors, valid_connections, route_current):

    passed_neighbors = []
    neighbor_weights = []

    if len(route_current) > 1:
        past_node = route_current[-2]
    else:
        past_node = None

    for neighbor in poss_neighbors:
        triangle_check_neighbors = valid_connections.loc[valid_connections.cell_id==neighbor, "vicinity"].values[0]
        # make this statement check if past_node exist check
        if past_node is not None and past_node in triangle_check_neighbors:
            continue
        else:
            passed_neighbors.append(neighbor)
            neighbor_weights.append(valid_connections.loc[valid_connections["cell_id"] == neighbor, "weight"].iloc[0])
    
    return passed_neighbors, neighbor_weights

def deadend_handeling(neighbor_nodes, route_current, min_stops, has_reversed):
    if not neighbor_nodes:
        if len(route_current) < min_stops and not has_reversed:
            route_current.reverse()
            return route_current, True, True

        # Cannot grow and already reversed once, so stop route
        return route_current, False, has_reversed

    return route_current, False, has_reversed

def crossover(parents, grid_neighbours, mutation_rate=0, valid_connections=None):
    '''
    needs to be done
    '''
    
    new_kid = {}
    index_list = random.sample(range(0, len(parents)), 2)  

    kid1_index = index_list[0]
    kid2_index = index_list[1]

    # It was -2 before, but i added the "Number of nodes", and all other metadata so now it is - 10
    number_of_routes = len(parents[0]) - 10
    
    for route in range(number_of_routes):
        the_choice = random.choice([1, 2])
        if the_choice == 1:
            the_route = parents[kid1_index][route]
            the_route = mutation_V2(the_route, mutation_rate, grid_neighbours, valid_connections)
            new_kid[route] = the_route
        else:
            the_route = parents[kid2_index][route]
            the_route = mutation_V2(the_route, mutation_rate, grid_neighbours, valid_connections)
            new_kid[route] = the_route

    return new_kid

def bfs_crossover(parents, grid_neighbours, mutation_rate=0, valid_connections=None):
    '''
    needs to be done
    '''
    
    new_kid = {}
    index_list = random.sample(range(0, len(parents)), 2)

    kid1_index = index_list[0]
    kid2_index = index_list[1]

    # New part
    route_keys = sorted(k for k in parents[0].keys() if isinstance(k, int))
    
    for route in route_keys:
        the_choice = random.choice([1, 2])
        if the_choice == 1:
            the_route = parents[kid1_index][route]
            the_route = mutation_V2(the_route, mutation_rate, grid_neighbours, valid_connections)
            new_kid[route] = the_route
        else:
            the_route = parents[kid2_index][route]
            the_route = mutation_V2(the_route, mutation_rate, grid_neighbours, valid_connections)
            new_kid[route] = the_route

    return new_kid

def mutation_V2(route, mutation_rate, grid_neighbours, valid_connections):
    ### "This whole function could be written nicer" - Jev
    mutation_cause = np.random.choice([True, False], size=1, p=[mutation_rate, 1-mutation_rate])

    # 1 = change end node
    # 2 = remove end node
    # 3 = add new node at the end
    if mutation_cause:
        if len(route) <= 2:
            which_mutation = np.random.choice([1, 3])
        else:
            which_mutation = np.random.choice([1, 2, 3])

        if which_mutation == 1:                   
            mutation_node = route[-2]
            removed_node = route[-1]
            if len(route) > 2:
                existing_neighbor = route[-3]
            else:
                existing_neighbor = None

            selected = grid_neighbours[grid_neighbours["cell_id"] == mutation_node]

            valid = selected["vicinity"].iloc[0]

            candidates = [n for n in valid if n not in (removed_node, existing_neighbor)]

            if not candidates:
                new_connection = route[-1]
            else:
                candidates, candidates_weight = TriangleCheck(candidates, valid_connections, route)
                if not candidates:
                    return route
                new_connection = random.choices(candidates, weights=candidates_weight, k=1)[0] 

            route[-1] = new_connection

        elif which_mutation == 2:
            route.pop()

        else:
            selected = grid_neighbours[grid_neighbours["cell_id"] == route[-1]]
            valid = selected["vicinity"].iloc[0]
            if len(valid) == 0:
                return route
            elif len(route) > 1:
                candidates = [n for n in valid if n != route[-2]]
            else:
                candidates = [n for n in valid]

            candidates, candidates_weight = TriangleCheck(candidates, valid_connections, route)
            if not candidates:
                    return route
            new_connection = random.choices(candidates, weights=candidates_weight, k=1)[0] 
            route.append(new_connection)

    return route

def generate_trip_weight(df, rangestart, rangestop):

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
    
    # Uncoment this to save pair combinations as dataframe
    #pair_df.to_csv("od_tabel") 
    
    return pair_df

def count_transfers(G, path):
    if len(path) < 2:
        return 0

    edge_routes = []

    for u, v in zip(path[:-1], path[1:]):
        edge_routes.append(G[u][v]["route"])

    transfers = 0

    for i in range(1, len(edge_routes)):
        if edge_routes[i] != edge_routes[i - 1]:
            transfers += 1

    return transfers

def normalize_generation(generation):
    
    nodes = []
    edges = []
    shortest_paths = []
    transfers = []

    for kid in generation.values():

        shortest_paths.append(kid["AVG_Shortest Path"])
        transfers.append(kid["Average transfers"])
        nodes.append(kid["Number of nodes"])
        edges.append(kid["Number of edges"])

    # min and max for each metric 
    min_nodes = min(nodes)
    max_nodes = max(nodes)
    
    min_edges = min(edges)
    max_edges = max(edges)
    
    min_short = min(shortest_paths)
    max_short = max(shortest_paths)

    min_transfer = min(transfers)
    max_transfer = max(transfers)

    for kid in generation.values():
        
        # lower is better
        kid["Edges_normalized"] = (
            (kid["Number of edges"] - min_edges)
            / (max_edges - min_edges)
        )
        
        kid["Nodes_normalized"] = (
            (kid["Number of nodes"] - min_nodes)
            / (max_nodes - min_nodes)
        )
       
        
        kid["Shortest_normalized"] = (
            (kid["AVG_Shortest Path"] - min_short)
            / (max_short - min_short)
        )

        kid["Transfer_normalized"] = (
            (kid["Average transfers"] - min_transfer)
            / (max_transfer - min_transfer)
        )
        
        # final score
        penalty = (
            0.10 * kid["Nodes_normalized"]
            + 0.35 * kid["Edges_normalized"]
            + 0.20 * kid["Transfer_normalized"]
            + 0.35 * kid["Shortest_normalized"]
        )

        coverage = kid["Score as %"] / 100
        kid["Final score"] = coverage * (1 - penalty)

    return generation

def allocate_population_to_hexagons(grid, postal_gdf, population_df,
                                    postal_code_col="postnummer",
                                    population_code_col="postal_code",
                                    population_col="population"):
    
    """
    Allocate postal-code population to hexagons by area overlap.

    Each hexagon gets:
        sum((intersection_area / postal_area) * postal_population)

    Parameters
    ----------
    grid : GeoDataFrame
        Hexagon polygons. Must contain 'cell_id'.
    postal_gdf : GeoDataFrame
        Postal code boundary polygons.
    population_df : DataFrame
        DataFrame with postal code and population.
    postal_code_col : str
        Column in postal_gdf with postal code.
    population_code_col : str
        Column in population_df with postal code.
    population_col : str
        Column in population_df with population.

    Returns
    -------
    grid_with_pop : GeoDataFrame
        Grid with a new column 'hex_population'.
    intersections : GeoDataFrame
        Intersection table for debugging/inspection.
    """

    # Copy so original objects are untouched
    grid = grid.copy()
    postal_gdf = postal_gdf.copy()
    population_df = population_df.copy()

    # Make sure postal-code columns have same type
    grid["cell_id"] = grid["cell_id"].astype(int)
    postal_gdf[postal_code_col] = postal_gdf[postal_code_col].astype(str)
    population_df[population_code_col] = population_df[population_code_col].astype(str)

    # Clean population column
    population_df[population_col] = pd.to_numeric(population_df[population_col], errors="coerce").fillna(0)

    # Merge population into postal polygons
    postal_gdf = postal_gdf.merge(
        population_df[[population_code_col, population_col]],
        left_on=postal_code_col,
        right_on=population_code_col,
        how="left"
    )

    postal_gdf[population_col] = postal_gdf[population_col].fillna(0)

    # Reproject postal polygons to same CRS as grid
    if postal_gdf.crs != grid.crs:
        postal_gdf = postal_gdf.to_crs(grid.crs)

    # Keep only polygons that intersect the grid area
    postal_gdf = postal_gdf[postal_gdf.intersects(grid.union_all())].copy()

    # Calculate total area of each postal polygon
    postal_gdf["postal_area"] = postal_gdf.geometry.area

    # Overlay = intersections between hexagons and postal code polygons
    intersections = gpd.overlay(
        grid[["cell_id", "geometry"]],
        postal_gdf[[postal_code_col, population_col, "postal_area", "geometry"]],
        how="intersection"
    )

    # Area of intersection
    intersections["intersection_area"] = intersections.geometry.area

    # Share of each postal code that lies inside each hexagon
    intersections["postal_share_in_hex"] = (
        intersections["intersection_area"] / intersections["postal_area"]
    )

    # Population contributed from postal code to hexagon
    intersections["pop_contribution"] = (
        intersections["postal_share_in_hex"] * intersections[population_col]
    )

    # Sum all postal-code contributions per hexagon
    hex_pop = (
        intersections.groupby("cell_id", as_index=False)["pop_contribution"]
        .sum()
        .rename(columns={"pop_contribution": "hex_population"})
    )

    # Attach to grid
    grid_with_pop = grid.merge(hex_pop, on="cell_id", how="left")
    grid_with_pop["hex_population"] = grid_with_pop["hex_population"].fillna(0)

    return grid_with_pop, intersections

def generate_trip_weight_V2(df, population_col="weight", seed=154):

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