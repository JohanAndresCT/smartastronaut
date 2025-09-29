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
    
    while queue:
        current_pos, samples_collected, fuel_left, has_ship, path, total_cost = queue.popleft()
        
        # Crear clave única para el estado visitado
        state_key = (current_pos, samples_collected, fuel_left, has_ship)
        
        if state_key in visited:
            continue
        visited.add(state_key)
        
        # ¿Hemos recolectado todas las muestras?
        if len(samples_collected) == len(samples_positions):
            return path, total_cost, samples_collected
        
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
            
            # Actualizar combustible y nave ANTES de calcular costo
            new_fuel = fuel_left
            new_has_ship = has_ship
            
            # Verificar si llega a la nave
            if new_pos == ship_pos and not has_ship:
                new_has_ship = True
                new_fuel = 20  # Combustible completo
                print(f"¡Astronauta subió a la nave en {new_pos}! Combustible: {new_fuel}")
            
            # Actualizar combustible si tiene nave
            if new_has_ship and new_fuel > 0:
                new_fuel = fuel_left - 1
            
            # Calcular costo del movimiento según el terreno y si tiene nave con combustible
            terrain_type = world[new_row][new_col]
            movement_cost = calcular_costo_movimiento(terrain_type, new_has_ship, new_fuel > 0)
            
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

def calcular_costo_movimiento(terrain_type, has_ship, has_fuel):
    # Con nave y combustible: costo reducido de 0.5 para cualquier terreno
    if has_ship and has_fuel:
        return 0.5
    
    # Costos normales a pie según el tipo de terreno
    if terrain_type == 0:    # Terreno libre
        return 1
    elif terrain_type == 2:  # Posición del astronauta (terreno libre)
        return 1  
    elif terrain_type == 3:  # Terreno rocoso
        return 3
    elif terrain_type == 4:  # Terreno volcánico
        return 5
    elif terrain_type == 5:  # Nave (sobre terreno libre)
        return 1
    elif terrain_type == 6:  # Muestra (sobre terreno libre)
        return 1
    else:
        return 1  # Por defecto (terreno libre)

"""
    Encuentra las posiciones del astronauta, nave y muestras en el mundo
    
    Returns:
        tuple: (pos_astronauta, pos_nave, lista_muestras)
"""

def encontrar_posiciones_especiales(world):
    astronaut_pos = None
    ship_pos = None
    samples = []
    
    for row in range(10):
        for col in range(10):
            if world[row][col] == 2:  # Astronauta
                astronaut_pos = (row, col)
            elif world[row][col] == 5:  # Nave
                ship_pos = (row, col)
            elif world[row][col] == 6:  # Muestra
                samples.append((row, col))
    
    return astronaut_pos, ship_pos, samples

"""
    Función principal para ejecutar la búsqueda por amplitud
    
    Args:
        world: matriz del mundo 10x10
    
    Returns:
        dict: resultado de la búsqueda con camino, costo y estadísticas
"""
def ejecutar_busqueda_amplitud(world):
    # Encontrar posiciones iniciales
    astronaut_pos, ship_pos, samples = encontrar_posiciones_especiales(world)
    
    if not astronaut_pos:
        return {"error": "No se encontró al astronauta en el mundo"}
    
    if not samples:
        return {"error": "No se encontraron muestras en el mundo"}
    
    print(f"Astronauta en: {astronaut_pos}")
    print(f"Nave en: {ship_pos}")
    print(f"Muestras en: {samples}")
    print("Iniciando búsqueda por amplitud...")
    
    # Ejecutar búsqueda
    result = search_path(world, astronaut_pos, samples)
    
    if result:
        path, total_cost, samples_collected = result
        
        print(f"\n🎯 ¡CAMINO ENCONTRADO!")
        print(f"📍 Pasos totales: {len(path) - 1}")
        print(f"💰 Costo total acumulado: {total_cost}")
        print(f"🔬 Muestras recolectadas: {len(samples_collected)}/{len(samples)}")
        print(f"🛤️  Camino completo: {path}")
        
        # Mostrar desglose de costos paso a paso
        print(f"\n📊 DESGLOSE DE COSTOS:")
        costo_acumulado = 0
        for i in range(1, len(path)):
            pos = path[i]
            terrain = world[pos[0]][pos[1]]
            
            # Simular cálculo de costo (simplificado para el desglose)
            if terrain == 0 or terrain == 2 or terrain == 5 or terrain == 6:
                costo_paso = 1
                tipo_terreno = "Libre"
            elif terrain == 3:
                costo_paso = 3
                tipo_terreno = "Rocoso"
            elif terrain == 4:
                costo_paso = 5  
                tipo_terreno = "Volcánico"
            else:
                costo_paso = 1
                tipo_terreno = "Libre"
            
            costo_acumulado += costo_paso
            print(f"  Paso {i}: {path[i-1]} → {pos} | {tipo_terreno} (+{costo_paso}) | Total: {costo_acumulado}")
        
        return {
            "success": True,
            "path": path,
            "total_cost": total_cost,
            "samples_collected": list(samples_collected),
            "steps": len(path) - 1,
            "algorithm": "Búsqueda por Amplitud (BFS)"
        }
    else:
        return {
            "success": False,
            "error": "No se encontró un camino para recolectar todas las muestras",
            "algorithm": "Búsqueda por Amplitud (BFS)"
        }