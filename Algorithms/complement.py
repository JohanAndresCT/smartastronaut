TERRAIN_COST = {
    0: 1,   # libre
    2: 1,   # astronauta
    3: 3,   # rocoso
    4: 5,   # volcánico
    5: 1,   # nave
    6: 1    # muestra+
}

Movements = {
    "up": (-1, 0),
    "down": (1, 0),
    "left": (0, -1),
    "right": (0, 1)
}

def in_bounds(grid,posAstroI,posAstroJ):
    if posAstroI >= 0 and posAstroI < len(grid) and posAstroJ >= 0 and posAstroJ < len(grid[0]):
        return True
    return False

def findAstro(grid):
    start = None
    found = False
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] == 2:
                start = (r, c)
                found = True
                break
        if found:
            break
    return start
def findSampling(grid):
    posSampling =[]
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] == 6:
                posSampling.append((r,c))
    return posSampling

def heuristics(posAstro, posSampling):
    bestHeur = float("inf")  
    posHeur = None            
    for sample in posSampling:
        dist = abs(posAstro[0] - sample[0]) + abs(posAstro[1] - sample[1])  # distancia Manhattan
        if dist < bestHeur:
            bestHeur = dist
            posHeur = sample
    
    return posHeur


def heuristic(posAstroI,posAstroJ, sample):

    distance = abs(posAstroI - sample[0]) + abs(posAstroJ - sample[1])

    return distance

def costMove(grid,posAstro):
    return TERRAIN_COST[grid[posAstro[0]][posAstro[1]]]


def reconstruct_path(node):
    path = []
    while node.parent is not None:
        path.append(node.action)
        node = node.parent
    return list(reversed(path))

def path_real(node_posI, node_posJ, moves):
    path = []
    for move in moves:
        node_posI += Movements[move][0]
        node_posJ += Movements[move][1]
        path.append((node_posI, node_posJ))
    return path


def is_goal(state, grid):
    return not findSampling(grid)  
