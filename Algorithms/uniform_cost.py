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
# Archivo: uniform_cost.py
# --------------------------------------------------------

import heapq
from Algorithms.breadth import calculate_movement_cost, find_special_positions

"""
Ejecuta búsqueda de costo uniforme para recolectar todas las muestras.

Args:
    world: matriz 10x10

Returns:
    dict similar to execute_breadth_search: {"success": bool, "path": [...], "total_cost": float, "algorithm": str}
"""
def execute_uniform_cost_search(world):
    start_pos, ship_pos, samples = find_special_positions(world)

    if not start_pos:
        return {"error": "No se encontró al astronauta en el mundo"}
    if not samples:
        return {"error": "No se encontraron muestras en el mundo"}

    # Cola de prioridad: (costo_total, pos, frozenset(muestras_recolectadas), combustible, tiene_nave, camino)
    heap = []
    initial = (0, start_pos, frozenset(), 0, False, [start_pos])
    heapq.heappush(heap, initial)
    visited = set()

    movements = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    nodes_expanded = 0
    max_depth = 0

    while heap:
        total_cost, current_pos, samples_collected, fuel_left, has_ship, path = heapq.heappop(heap)
        nodes_expanded += 1
        max_depth = max(max_depth, len(path) - 1)

        state_key = (current_pos, samples_collected, fuel_left, has_ship)
        if state_key in visited:
            continue
        visited.add(state_key)

    # Comprobar objetivo
        if len(samples_collected) == len(samples):
            return {"success": True, "path": path, "total_cost": total_cost, "nodes_expanded": nodes_expanded, "max_depth": max_depth, "algorithm": "Costo Uniforme"}

        for dr, dc in movements:
            nr, nc = current_pos[0] + dr, current_pos[1] + dc
            if not (0 <= nr < 10 and 0 <= nc < 10):
                continue
            if world[nr][nc] == 1:
                continue

            new_pos = (nr, nc)


            # Calcular el costo de movimiento usando el estado previo (por lo que subir a la nave NO otorga costo reducido en la misma transición)
            terrain_type = world[nr][nc]
            move_cost = calculate_movement_cost(terrain_type, has_ship, fuel_left > 0)

            # Actualizar estado de nave/combustible para el NUEVO estado después del movimiento
            new_has_ship = has_ship
            new_fuel = fuel_left

            if not has_ship and new_pos == ship_pos:
                new_has_ship = True
                new_fuel = 20  # Combustible completo al subir (la reducción empieza en el siguiente movimiento)
            elif has_ship:
                # consumir una unidad de combustible para este movimiento (afecta al nuevo estado)
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

            new_state = (new_total_cost, new_pos, frozenset(new_samples), new_fuel, new_has_ship, new_path)
            heapq.heappush(heap, new_state)

    return {"success": False, "error": "No se encontró un camino para recolectar todas las muestras", "algorithm": "Costo Uniforme"}
