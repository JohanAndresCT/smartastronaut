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
# Archivo: depth.py
# --------------------------------------------------------


from collections import deque
from Algorithms.breadth import calculate_movement_cost, find_special_positions

"""
Implementa búsqueda en profundidad (DFS) para el astronauta

Args:
    world: matriz 10x10 del mundo
    start_pos: tupla (fila, columna) posición inicial del astronauta (determinada desde `world`)
    samples_positions: lista de tuplas con posiciones de las muestras (determinadas desde `world`)

Returns:
    dict: resultado con claves similares a las de otras búsquedas:
        {"success": bool, "path": [...], "total_cost": float, "nodes_expanded": int, "max_depth": int, "algorithm": str}

Nota: DFS no garantiza costo mínimo; devuelve la primera solución encontrada.
"""
def execute_depth_search(world):
    start_pos, ship_pos, samples = find_special_positions(world)

    if not start_pos:
        return {"error": "No se encontró al astronauta en el mundo"}
    if not samples:
        return {"error": "No se encontraron muestras en el mundo"}

    # Entradas de la pila: (pos, conjunto_muestras_recolectadas, combustible, tiene_nave, camino, costo_total)
    stack = [(start_pos, frozenset(), 0, False, [start_pos], 0)]
    visited = set()
    nodes_expanded = 0
    max_depth = 0

    movements = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while stack:
        current_pos, samples_collected, fuel_left, has_ship, path, total_cost = stack.pop()
        nodes_expanded += 1
        max_depth = max(max_depth, len(path) - 1)

        state_key = (current_pos, samples_collected, fuel_left, has_ship)
        if state_key in visited:
            continue
        visited.add(state_key)

        if len(samples_collected) == len(samples):
            return {"success": True, "path": path, "total_cost": total_cost, "nodes_expanded": nodes_expanded, "max_depth": max_depth, "algorithm": "Profundidad"}

        for dr, dc in movements:
            nr, nc = current_pos[0] + dr, current_pos[1] + dc
            if not (0 <= nr < 10 and 0 <= nc < 10):
                continue
            if world[nr][nc] == 1:
                continue

            new_pos = (nr, nc)

            # Usar el estado previo para calcular el costo de movimiento (hacer boarding no reduce el costo en la misma transición)
            terrain_type = world[nr][nc]
            move_cost = calculate_movement_cost(terrain_type, has_ship, fuel_left > 0)

            # Actualizar estado de nave/combustible para el siguiente estado
            new_has_ship = has_ship
            new_fuel = fuel_left

            if not has_ship and new_pos == ship_pos:
                new_has_ship = True
                new_fuel = 20
            elif has_ship:
                if fuel_left > 0:
                    new_fuel = fuel_left - 1
                else:
                    new_has_ship = False
                    new_fuel = 0

            new_samples = samples_collected
            if new_pos in samples and new_pos not in samples_collected:
                new_samples = samples_collected | {new_pos}

            new_path = path + [new_pos]
            new_total_cost = total_cost + move_cost

            stack.append((new_pos, frozenset(new_samples), new_fuel, new_has_ship, new_path, new_total_cost))

    return {"success": False, "error": "No se encontró una solución con DFS", "algorithm": "Profundidad"}
