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
# Archivo: breadth.py
# --------------------------------------------------------

from collections import deque

"""
    Implementa búsqueda en amplitud (BFS) para el astronauta
    
    Args:
        world: matriz 10x10 del mundo
        start_pos: tupla (fila, columna) posición inicial del astronauta
        samples_positions: lista de tuplas con posiciones de las muestras
    
    Returns:
        tuple: (camino_encontrado, costo_total, muestras_recolectadas) o None si no hay solución
"""

def search_path(world, start_pos, samples_positions):
    # Encontrar posición de la nave
    ship_pos = None
    for row in range(10):
        for col in range(10):
            if world[row][col] == 5:  # Nave
                ship_pos = (row, col)
                break
    
    # Estado inicial: (posicion, muestras_recolectadas, combustible_nave, tiene_nave, camino, costo_total)
    # El costo inicial es 0 porque aún no se ha movido
    initial_state = (start_pos, frozenset(), 0, False, [start_pos], 0)
    
    queue = deque([initial_state])
    visited = set()
    
    # Movimientos posibles: arriba, abajo, izquierda, derecha
    movements = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    nodes_expanded = 0
    max_depth = 0

    while queue:
        current_pos, samples_collected, fuel_left, has_ship, path, total_cost = queue.popleft()
        nodes_expanded += 1
        max_depth = max(max_depth, len(path) - 1)
        
        # Crear clave única para el estado visitado
        state_key = (current_pos, samples_collected, fuel_left, has_ship)
        
        if state_key in visited:
            continue
        visited.add(state_key)
        
        # ¿Hemos recolectado todas las muestras?
        if len(samples_collected) == len(samples_positions):
                # Incluir métricas
                return path, total_cost, samples_collected, nodes_expanded, max_depth
        
        # Explorar todos los movimientos posibles
        for dr, dc in movements:
            new_row, new_col = current_pos[0] + dr, current_pos[1] + dc
            new_pos = (new_row, new_col)
            
            # Verificar límites del mundo
            if not (0 <= new_row < 10 and 0 <= new_col < 10):
                continue
                
            # Verificar si es un obstáculo
            if world[new_row][new_col] == 1:  # Obstáculo
                continue
            
            # Calcular costo del movimiento según el terreno y el estado PREVIO (antes de la transición)
            terrain_type = world[new_row][new_col]
            movement_cost = calculate_movement_cost(terrain_type, has_ship, fuel_left > 0)

            # Actualizar combustible y nave para el NUEVO estado después del movimiento
            new_fuel = fuel_left
            new_has_ship = has_ship

            # Verificar si llega a la nave (boarding da fuel pero no reduce el costo de esta transición)
            if new_pos == ship_pos and not has_ship:
                new_has_ship = True
                new_fuel = 20  # Combustible completo
                print(f"¡Astronauta subió a la nave en {new_pos}! Combustible: {new_fuel}")

            # Actualizar combustible si ya tenía nave (consumir 1 unidad para el nuevo estado)
            if has_ship:
                if fuel_left > 0:
                    new_fuel = fuel_left - 1
                else:
                    new_has_ship = False
                    new_fuel = 0
            
            # Verificar si recoge una muestra
            new_samples = samples_collected
            if new_pos in samples_positions and new_pos not in samples_collected:
                new_samples = samples_collected | {new_pos}
                print(f"¡Muestra recolectada en {new_pos}! Total: {len(new_samples)}/{len(samples_positions)}")
            
            # Crear nuevo estado con costo acumulado
            new_path = path + [new_pos]
            new_total_cost = total_cost + movement_cost
            new_state = (new_pos, new_samples, new_fuel, new_has_ship, new_path, new_total_cost)
            
            queue.append(new_state)
    
    return None  # No se encontró solución

"""
    Calcula el costo de moverse a una casilla según el terreno y si tiene nave con combustible
    
    Args:
        terrain_type: tipo de terreno (0=libre, 1=obstáculo, 2=astronauta, 3=rocoso, 4=volcánico, 5=nave, 6=muestra)
        has_ship: si el astronauta tiene la nave
        has_fuel: si la nave tiene combustible
    
    Returns:
        float: costo del movimiento
"""

def calculate_movement_cost(terrain_type, has_ship, has_fuel):
    # With ship and fuel: reduced cost of 0.5 for any terrain
    if has_ship and has_fuel:
        return 0.5

    # Normal walking costs according to terrain type
    if terrain_type == 0:    # Free terrain
        return 1
    elif terrain_type == 2:  # Astronaut position (free terrain)
        return 1
    elif terrain_type == 3:  # Rocky terrain
        return 3
    elif terrain_type == 4:  # Volcanic terrain
        return 5
    elif terrain_type == 5:  # Ship (on free terrain)
        return 1
    elif terrain_type == 6:  # Sample (on free terrain)
        return 1
    else:
        return 1  # Default (free terrain)

"""
    Encuentra las posiciones del astronauta, nave y muestras en el mundo
    
    Returns:
        tuple: (pos_astronauta, pos_nave, lista_muestras)
"""
def find_special_positions(world):
    astronaut_pos = None
    ship_pos = None
    samples = []

    for row in range(10):
        for col in range(10):
            if world[row][col] == 2:  # Astronaut
                astronaut_pos = (row, col)
            elif world[row][col] == 5:  # Ship
                ship_pos = (row, col)
            elif world[row][col] == 6:  # Sample
                samples.append((row, col))

    return astronaut_pos, ship_pos, samples

"""
    Función principal para ejecutar la búsqueda por amplitud
    
    Args:
        world: matriz del mundo 10x10
    
    Returns:
        dict: resultado de la búsqueda con camino, costo y estadísticas
"""
def execute_breadth_search(world):
    # Find initial positions
    astronaut_pos, ship_pos, samples = find_special_positions(world)
    
    if not astronaut_pos:
        return {"error": "No se encontró al astronauta en el mundo"}
    
    if not samples:
        return {"error": "No se encontraron muestras en el mundo"}
    
    print(f"Astronauta en: {astronaut_pos}")
    print(f"Nave en: {ship_pos}")
    print(f"Muestras en: {samples}")
    print("Iniciando búsqueda por amplitud...")
    
    # Run the search
    result = search_path(world, astronaut_pos, samples)
    
    if result:
    # Desempaquetar resultado con métricas opcionales
        if len(result) == 3:
            path, total_cost, samples_collected = result
            nodes_expanded = None
            max_depth = None
        else:
            path, total_cost, samples_collected, nodes_expanded, max_depth = result
        
        print(f"\n ¡CAMINO ENCONTRADO!")
        print(f" Pasos totales: {len(path) - 1}")
        print(f"Costo total acumulado: {total_cost}")
        print(f" Muestras recolectadas: {len(samples_collected)}/{len(samples)}")
        print(f" Camino completo: {path}")
        
        # Mostrar desglose de costos paso a paso usando la misma lógica que el algoritmo
        print(f"\n DESGLOSE DE COSTOS (cálculo real con nave/combustible):")
        costo_acumulado = 0.0
        has_ship = False
        fuel = 0

        for i in range(1, len(path)):
            prev = path[i-1]
            pos = path[i]
            terrain = world[pos[0]][pos[1]]

            # Calculate step cost using the PREVIOUS state (has_ship, fuel>0)
            step_cost = calculate_movement_cost(terrain, has_ship, fuel > 0)

            # Mapear tipo de terreno para visualización
            if terrain == 3:
                tipo_terreno = "Rocoso"
            elif terrain == 4:
                tipo_terreno = "Volcánico"
            else:
                tipo_terreno = "Libre"

            costo_acumulado += step_cost
            print(f"  Paso {i}: {prev} → {pos} | {tipo_terreno} (+{step_cost}) | Total: {costo_acumulado}")

            # Actualizar estado tras moverse al nuevo estado (boarding/consumo)
            if not has_ship and terrain == 5:
                has_ship = True
                fuel = 20
            elif has_ship:
                if fuel > 0:
                    fuel -= 1
                else:
                    has_ship = False
                    fuel = 0
        
        out = {
            "success": True,
            "path": path,
            "total_cost": total_cost,
            "samples_collected": list(samples_collected),
            "steps": len(path) - 1,
            "algorithm": "Búsqueda por Amplitud (BFS)"
        }
        if 'nodes_expanded' in locals() and nodes_expanded is not None:
            out['nodes_expanded'] = nodes_expanded
            out['max_depth'] = max_depth
        return out
    else:
        return {
            "success": False,
            "error": "No se encontró un camino para recolectar todas las muestras",
            "algorithm": "Búsqueda por Amplitud (BFS)"
        }