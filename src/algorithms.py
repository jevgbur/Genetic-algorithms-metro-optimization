import pandas as pd
import random
import numpy as np
import networkx as nx
from itertools import combinations
import geopandas as gpd

def extension_cal_scoreV2(G, od_df, neighbor_df, pair_weights, G_metro=None):
    '''
    This function calculates the score of a given network design (G) based on demand coverage, 
    average shortest path length, and average transfers. It can also incorporate an existing metro network (G_metro) 
    into the evaluation.      
    '''
    # combine existing metro + candidate network
    if G_metro is not None:
        evaluation_graph = G_metro.copy()
        evaluation_graph.add_nodes_from(G.nodes(data=True))
        evaluation_graph.add_edges_from(G.edges(data=True))
    else:
        evaluation_graph = G.copy()

    # demand coverage graph should also include existing metro + candidate
    demand_graph = evaluation_graph.copy()

    vicinity_lookup = neighbor_df.set_index("cell_id")["vicinity"].to_dict()

    nodes_to_add = set()
    for node in evaluation_graph.nodes():
        nodes_to_add.update(vicinity_lookup.get(node, []))

    demand_graph.add_nodes_from(nodes_to_add)

    temp_score = 0
    pairs = list(combinations(demand_graph.nodes(), 2))

    for node1, node2 in pairs:
        key = (min(node1, node2), max(node1, node2))
        temp_score += pair_weights.get(key, 0)

    total_demand = od_df["weight"].sum()
    evaluation_score = (temp_score / total_demand) * 100

    shortest_paths = dict(nx.shortest_path(evaluation_graph))

    total_path_length = 0
    total_pairs = 0
    total_transfers = 0

    for origin in shortest_paths:
        for destination in shortest_paths[origin]:
            if origin == destination:
                continue

            path = shortest_paths[origin][destination]
            path_length = len(path) - 1
            transfers = count_transfers(evaluation_graph, path)

            total_path_length += path_length
            total_pairs += 1
            total_transfers += transfers

    average_shortest_path = total_path_length / total_pairs
    average_transfers = total_transfers / total_pairs

    return evaluation_score, average_shortest_path, average_transfers

def cal_scoreV2(G, od_df, neighbor_df, pair_weights): 
    '''
    This function calculates the score of a given network design (G) based on demand coverage, 
    average shortest path length, and average transfers.
    '''
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
    '''
    Selects parent solutions for the next generation based on their performance.
    '''
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

def extension_TriangleCheck(poss_neighbors, valid_connections, route_current, G_metro):
    '''
    Checks for triangular connections in the route.
    '''
    curr_node = route_current[-1]
    
    passed_neighbors = []
    neighbor_weights = []

    if len(route_current) > 1:
        past_node = route_current[-2]
    else:
        past_node = None

    for neighbor in poss_neighbors:
        # check if neighbor is already connected to current node in G_metro, if so skip
        if (curr_node, neighbor) in G_metro.edges() or (neighbor, curr_node) in G_metro.edges():
            continue
        else:
            triangle_check_neighbors = valid_connections.loc[valid_connections.cell_id==neighbor, "vicinity"].values[0]
            # make this statement check if past_node exist check
            if past_node is not None and past_node in triangle_check_neighbors:
                continue
            else:
                passed_neighbors.append(neighbor)
                neighbor_weights.append(valid_connections.loc[valid_connections["cell_id"] == neighbor, "weight"].iloc[0])
    
    return passed_neighbors, neighbor_weights

def TriangleCheck(poss_neighbors, valid_connections, route_current):
    '''
    Checks for triangular connections in the route.
    '''
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
    '''
    This function handles dead-ends in the route. 
    If there are no neighboring nodes to extend the route, it checks if the current route has fewer stops than the 
    minimum required. If so, it reverses the route and allows for one more extension attempt. 
    If there are still no neighbors after reversing, it stops the route.
    '''
    if not neighbor_nodes:
        if len(route_current) < min_stops and not has_reversed:
            route_current.reverse()
            return route_current, True, True

        # Cannot grow and already reversed once, so stop route
        return route_current, False, has_reversed

    return route_current, False, has_reversed

def extenstion_crossover(parents, grid_neighbours, mutation_rate=0, valid_connections=None, G_metro=None):
    '''
     This crossover function uses a breadth-first search approach to combine routes from two parent solutions.
     It randomly selects two parent solutions and iterates through their routes. For each route, it randomly decides
     whether to take the route from the first or second parent. 
     It then applies mutation to the selected route before adding it to the new child solution. 
     
     This method allows for a more diverse combination of routes while still 
     incorporating mutation to explore new possibilities.
     '''
    
    new_kid = {}

    index_list = random.sample(range(0, len(parents)), 2)  

    kid1_index = index_list[0]
    kid2_index = index_list[1]

    route_keys = sorted(k for k in parents[0].keys() if isinstance(k, int))
    
    for route in route_keys:
        the_choice = random.choice([1, 2])
        if the_choice == 1:
            the_route = parents[kid1_index][route]
            the_route = extenstion_mutation(the_route, mutation_rate, grid_neighbours, valid_connections, G_metro)
            new_kid[route] = the_route
        else:
            the_route = parents[kid2_index][route]
            the_route = extenstion_mutation(the_route, mutation_rate, grid_neighbours, valid_connections, G_metro)
            new_kid[route] = the_route

    return new_kid

def crossover(parents, grid_neighbours, mutation_rate=0, valid_connections=None):
    '''
     This crossover function uses a breadth-first search approach to combine routes from two parent solutions.
     It randomly selects two parent solutions and iterates through their routes. For each route, it randomly decides
     whether to take the route from the first or second parent. 
     It then applies mutation to the selected route before adding it to the new child solution. 
     
     This method allows for a more diverse combination of routes while still 
     incorporating mutation to explore new possibilities.
     '''
    new_kid = {}
    index_list = random.sample(range(0, len(parents)), 2)  

    kid1_index = index_list[0]
    kid2_index = index_list[1]

    # It was -2 before, but because of metadata added it is -10
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
     This crossover function uses a breadth-first search approach to combine routes from two parent solutions.
     It randomly selects two parent solutions and iterates through their routes. For each route, it randomly decides
     whether to take the route from the first or second parent. 
     It then applies mutation to the selected route before adding it to the new child solution. 
     
     This method allows for a more diverse combination of routes while still 
     incorporating mutation to explore new possibilities.
     '''
    
    new_kid = {}
    index_list = random.sample(range(0, len(parents)), 2)

    kid1_index = index_list[0]
    kid2_index = index_list[1]

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

def extenstion_mutation(route, mutation_rate, grid_neighbours, valid_connections, G_metro):
    '''
    This function applies mutation to a given route. 
    The mutation can be one of three types: 
    - changing the end node
    - removing the end node
    - adding a new node at the end. 
    '''

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
            #placement = "end"

            selected = grid_neighbours[grid_neighbours["cell_id"] == mutation_node]

            valid = selected["vicinity"].iloc[0]

            candidates = [n for n in valid if n not in (removed_node, existing_neighbor)]

            if not candidates:
                new_connection = route[-1]
            else:
                candidates, candidates_weight = extension_TriangleCheck(candidates, valid_connections, route, G_metro)
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
            
            candidates, candidates_weight = extension_TriangleCheck(candidates, valid_connections, route, G_metro)
            if not candidates:
                    return route
            new_connection = random.choices(candidates, weights=candidates_weight, k=1)[0] 
            route.append(new_connection)


    return route

def mutation_V2(route, mutation_rate, grid_neighbours, valid_connections):
    '''
    This function applies mutation to a given route. 
    The mutation can be one of three types: 
    - changing the end node
    - removing the end node
    - adding a new node at the end. 
    '''
    
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


def count_transfers(G, path):
    '''
    This function counts the number of transfers in a given path.
    A transfer is counted whenever the "route" attribute of the edges changes along the path.
    '''
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
    '''
    This function normalizes the metrics of the generation and calculates a final score for each solution.
    '''
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
    
    '''
    This function allocates population to hexagonal grid cells based on the intersection of postal code polygons 
    and the hexagonal grid. It calculates the share of each postal code's population that falls within each hexagon 
    and sums these contributions to get the total population for each hexagon. It returns the grid with an added 
    "hex_population" column and a GeoDataFrame of the intersections for further analysis if needed.
    '''
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

