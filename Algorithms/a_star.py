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
# Archivo: a_star.py
# --------------------------------------------------------

import heapq
import random
from Algorithms.objects import Node
from itertools import count
from Algorithms.complement import findAstro, findSampling, in_bounds,path_real
from Algorithms.complement import costMove, reconstruct_path,heuristics, heuristic

"""
Ejecuta búsqueda A* (informada) para recolectar todas las muestras.

Args:
    grid: matriz del mundo (por ejemplo 10x10)

Returns:
    dict con formato similar a otros algoritmos: {"success": bool, "path": [...], "total_cost": float, "algorithm": str}
"""


def a_star(grid):
    nodes = []
    visited = set()
    counter = count()
    collected_samples = set()

    root = Node (findAstro(grid))
    root.hPost = heuristics(root.state, findSampling(grid))
    root.h = heuristic(root.state[0], root.state[1], root.hPost)
    root.path_cost = 0
    root.f = root.h

    def push_child(new_pos, action, rocket_status, parent_node):
        hPost = heuristics(new_pos, findSampling(grid))
        h = heuristic(new_pos[0], new_pos[1], hPost)

        
        if grid[new_pos[0]][new_pos[1]] == 5:
            rocket_status = True
            rocket_fuel = 20
            visited.clear()
        elif parent_node.rocket:
            rocket_status = True
            rocket_fuel = parent_node.rocketFuel - 1
            if rocket_fuel == 0:
                rocket_status = False
                rocket_fuel = 0
        else:
            rocket_status = False
            rocket_fuel = 0

        
        if rocket_status:
            path_cost = parent_node.path_cost + 0.5
        else:
            path_cost = parent_node.path_cost + costMove(grid, new_pos)

        child = Node(
            state=new_pos,
            parent=parent_node,
            action=action,
            hPost=hPost,
            h=h,
            path_cost=path_cost,
            f=path_cost + h / 2,
            rocket=rocket_status,
            rocketFuel=rocket_fuel
        )

        heapq.heappush(nodes, (child.f, next(counter), child))

    
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

        state_key = (current.state, current.rocket, current.rocketFuel)
        if state_key in visited:
            continue
        visited.add(state_key)

        
        if grid[current.state[0]][current.state[1]] == 5 and not current.rocket:
            current.rocket = True
            current.rocketFuel = 20
            visited.clear()
            nodes.clear()
            current.f = current.path_cost + current.h / 2
            heapq.heappush(nodes, (current.f, next(counter), current))
            continue

        
        if grid[current.state[0]][current.state[1]] == 6 and current.state not in collected_samples:
            collected_samples.add(current.state)
            remaining = [p for p in findSampling(grid) if p not in collected_samples]
            print("Samples collected:", collected_samples)
            if not remaining:
                    pathA=path_real(findAstro(grid)[0], findAstro(grid)[1], reconstruct_path(current))
                    return {"success":True,"path":pathA,"total_cost":current.path_cost,"algorithm":"a_star"}

            
            nodes.clear()
            visited.clear()
            current.hPost = heuristics(current.state, remaining)
            current.h = heuristic(current.state[0], current.state[1], current.hPost)
            current.f = current.path_cost + current.h / 2
            heapq.heappush(nodes, (current.f, next(counter), current))

            
            if in_bounds(grid, current.state[0]-1, current.state[1]) and grid[current.state[0]-1][current.state[1]] != 1:
                push_child((current.state[0]-1, current.state[1]), "up", current.rocket, current)
            if in_bounds(grid, current.state[0]+1, current.state[1]) and grid[current.state[0]+1][current.state[1]] != 1:
                push_child((current.state[0]+1, current.state[1]), "down", current.rocket, current)
            if in_bounds(grid, current.state[0], current.state[1]-1) and grid[current.state[0]][current.state[1]-1] != 1:
                push_child((current.state[0], current.state[1]-1), "left", current.rocket, current)
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
