# --------------------------------------------------------
# Proyecto de inteligencia Artificial - Smart astronaut
# Integrantes: 
# Dylan Fernando Morales Rojas (2338330)
# Johan Andres Ceballos Tabarez (2372229)
#
# Universidad: Universidad del Valle
# Profesor: Oscar Bedoya
#
# Fecha de creación: 23 de septiembre del 2025
# Última modificación: 24 de octubre del 2025
#
# Archivo: greedy.py
# --------------------------------------------------------

import heapq
import random
from Algorithms.objects import Node
from itertools import count
from Algorithms.complement import findAstro, findSampling, in_bounds,path_real
from Algorithms.complement import costMove, reconstruct_path,heuristics, heuristic

"""
Ejecuta búsqueda voraz (greedy) informada por heurística para recolectar todas las muestras.

Args:
    grid: matriz del mundo (por ejemplo 10x10)

Returns:
    dict con formato similar a otros algoritmos: {"success": bool, "path": [...], "total_cost": float, "nodes_expanded": int, "max_depth": int, "algorithm": str}
"""

def greedy_search(grid):
    nodes = []
    visited = set()
    collected_samples = set()
    nodes_expanded = 0
    max_depth = 0

    root = Node(findAstro(grid))
    root.hPost = heuristics(root.state, findSampling(grid))
    root.h = heuristic(root.state[0], root.state[1], root.hPost)

    def push_child(new_pos, action,rocket_status,parent_node):

        hPost = heuristics(new_pos, findSampling(grid))
        h = heuristic(new_pos[0], new_pos[1], hPost)
        # Determine child's rocket status and fuel (state after the move)
        if grid[new_pos[0]][new_pos[1]] == 5:
            rocket_status = True
            rocket_fuel = 20
        elif parent_node.rocket:
            rocket_status = True
            rocket_fuel = parent_node.rocketFuel - 1
            if rocket_fuel <= 0:
                rocket_status = False
                rocket_fuel = 0
        else:
            rocket_status = False
            rocket_fuel = 0

        # Movement cost is based on the parent's rocket state (i.e., whether the agent
        # had a working rocket before making this move). Boarding should not reduce
        # the cost of the same transition that picked up the rocket.
        if parent_node.rocket and parent_node.rocketFuel > 0:
            move_cost = 0.5
        else:
            move_cost = costMove(grid, new_pos)

        child = Node(
            state=new_pos,
            parent=parent_node,
            action=action,
            hPost=hPost,
            h=h/2,
            path_cost=parent_node.path_cost + move_cost,
            rocket=rocket_status,
            rocketFuel=rocket_fuel
        )
        heapq.heappush(nodes, (child.h, random.random(), child))
    
    if in_bounds(grid, root.state[0]-1, root.state[1]) and grid[root.state[0]-1][root.state[1]] != 1:
        push_child((root.state[0]-1, root.state[1]), "up", False, root)
    if in_bounds(grid, root.state[0]+1, root.state[1]) and grid[root.state[0]+1][root.state[1]] != 1:
        push_child((root.state[0]+1, root.state[1]), "down", False, root)
    if in_bounds(grid, root.state[0], root.state[1]-1) and grid[root.state[0]][root.state[1]-1] != 1:
        push_child((root.state[0], root.state[1]-1), "left", False, root)
    if in_bounds(grid, root.state[0], root.state[1]+1) and grid[root.state[0]][root.state[1]+1] != 1:
        push_child((root.state[0], root.state[1]+1), "right", False, root)

    while nodes:

        _, _, current = heapq.heappop(nodes)
        nodes_expanded += 1
        # try to compute depth from current
        try:
            moves = reconstruct_path(current)
            pathA = path_real(findAstro(grid)[0], findAstro(grid)[1], moves)
            max_depth = max(max_depth, len(pathA) - 1)
        except Exception:
            pass

        if current.state in visited:
            continue
        visited.add(current.state)
        
        if current.state in collected_samples:
            continue

  
        if current.state in findSampling(grid) and current.state not in collected_samples:
            collected_samples.add(current.state)

            if len(collected_samples) == len(findSampling(grid)):
                pathA = path_real(findAstro(grid)[0], findAstro(grid)[1], reconstruct_path(current))
                return {"success": True, "path": pathA, "total_cost": current.path_cost, "nodes_expanded": nodes_expanded, "max_depth": max_depth, "algorithm": "greedy_search"}
            
            rocket_status = current.rocket
            rocket_fuel = current.rocketFuel
            nodes.clear()
            visited.clear()
            current.rocket = rocket_status
            current.rocketFuel = rocket_fuel


            current.hPost = heuristics(current.state, [p for p in findSampling(grid) if p not in collected_samples])
            current.h = heuristic(current.state[0], current.state[1], current.hPost)
            #Arriba
            if in_bounds(grid, current.state[0]-1, current.state[1]) and grid[current.state[0]-1][current.state[1]] != 1:
                push_child((current.state[0]-1, current.state[1]), "up", current.rocket, current)
            #Abajo
            if in_bounds(grid, current.state[0]+1, current.state[1]) and grid[current.state[0]+1][current.state[1]] != 1:
                push_child((current.state[0]+1, current.state[1]), "down", current.rocket, current)
            #Izquierda
            if in_bounds(grid, current.state[0], current.state[1]-1) and grid[current.state[0]][current.state[1]-1] != 1:
                push_child((current.state[0], current.state[1]-1), "left", current.rocket, current)
            #Derecha
            if in_bounds(grid, current.state[0], current.state[1]+1) and grid[current.state[0]][current.state[1]+1] != 1:
                push_child((current.state[0], current.state[1]+1), "right", current.rocket, current)

            continue
   
        if in_bounds(grid, current.state[0]-1, current.state[1]) and grid[current.state[0]-1][current.state[1]] != 1:
            push_child((current.state[0]-1, current.state[1]), "up", current.rocket, current)
        if in_bounds(grid, current.state[0]+1, current.state[1]) and grid[current.state[0]+1][current.state[1]] != 1:
            push_child((current.state[0]+1, current.state[1]), "down", current.rocket, current)
        if in_bounds(grid, current.state[0], current.state[1]-1) and grid[current.state[0]][current.state[1]-1] != 1:
            push_child((current.state[0], current.state[1]-1), "left", current.rocket, current)
        if in_bounds(grid, current.state[0], current.state[1]+1) and grid[current.state[0]][current.state[1]+1] != 1:
            push_child((current.state[0], current.state[1]+1), "right", current.rocket, current)
    return 0
