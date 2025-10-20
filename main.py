import pygame
import sys
import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageSequence
from Algorithms.breadth import ejecutar_busqueda_amplitud, calcular_costo_movimiento
from Algorithms.greedy import greedy_search
from Algorithms.a_star import a_star
from Algorithms.objects import Node

 

pygame.init()
pygame.mixer.init()  # Inicializar el sistema de audio

# Window setup
size = (600, 700)  # Increased from 500x500 to give more space
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Smart Astronaut")

# Cargar y reproducir música de fondo
try:
    pygame.mixer.music.load("Sounds/maintheme.mp3")
    pygame.mixer.music.set_volume(0.3)  # Volumen al 30%
    pygame.mixer.music.play(-1)  # -1 significa reproducir en bucle infinito
    print("Música de fondo cargada exitosamente!")
except Exception as e:
    print(f"Error cargando música de fondo: {e}")

# Cargar efectos de sonido
try:
    sample_sound = pygame.mixer.Sound("Sounds/grabsample.ogg")
    sample_sound.set_volume(0.5)  # Volumen al 50%
    print("Sonido de muestra cargado exitosamente!")
except Exception as e:
    print(f"Error cargando sonido de muestra: {e}")
    sample_sound = None

try:
    ship_sound = pygame.mixer.Sound("Sounds/shiptrue.mp3")
    ship_sound.set_volume(0.4)  # Volumen al 40%
    print("Sonido de nave cargado exitosamente!")
except Exception as e:
    print(f"Error cargando sonido de nave: {e}")
    ship_sound = None

# Game states
TITLE_SCREEN = 0
GAME_SCREEN = 1
SELECT_ALGORITHM_SCREEN = 2
SELECT_UNINFORMED_SCREEN = 3
SELECT_INFORMED_SCREEN = 4
SIMULATION_SCREEN = 5
current_state = TITLE_SCREEN

# Algorithm selection variables
selected_algorithm_type = None  # "uninformed" or "informed"
selected_algorithm = None       # specific algorithm name

# Animation variables
algorithm_path = []            # Camino encontrado por el algoritmo
current_step = 0               # Paso actual en la animación
astronaut_pos = (1, 2)         # Posición actual del astronauta
animation_speed = 30           # Frames entre cada paso (más bajo = más rápido)
animation_counter = 0          # Contador para controlar la velocidad
is_animating = False           # Si está en proceso de animación
collected_samples = set()      # Muestras ya recolectadas
algorithm_result = None        # Resultado completo del algoritmo
current_cost = 0               # Costo acumulado actual en la animación
has_ship = False               # Si el astronauta tiene la nave en la animación
fuel_left = 0                  # Combustible restante en la animación

# Astronaut animation variables
astronaut_sprites = []         # Lista de sprites del astronauta corriendo
astronaut_sprites_flipped = [] # Sprites invertidos para movimiento izquierda
current_sprite_index = 0       # Índice del sprite actual (0-4)
astronaut_direction = "right"  # Dirección del movimiento ("right" o "left")
animation_completed = False    # Si la animación ha terminado completamente
original_world = []            # Copia del mundo original para restaurar terrenos

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GRAY = (169, 169, 169)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

# Initialize world with default values
world = [
    [0, 5, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 0, 1, 1, 1, 0, 1, 0],
    [0, 2, 0, 0, 3, 3, 3, 6, 0, 0],
    [0, 1, 0, 1, 1, 1, 1, 0, 1, 1],
    [0, 1, 0, 1, 0, 0, 0, 0, 1, 1],
    [0, 1, 0, 1, 4, 1, 1, 1, 1, 1],
    [0, 0, 6, 4, 4, 0, 0, 1, 1, 1],
    [1, 0, 1, 1, 0, 1, 0, 1, 0, 6],
    [0, 0, 0, 0, 0, 1, 0, 1, 0, 1],
    [0, 1, 1, 1, 0, 0, 0, 0, 0, 1]
]

# Fonts
title_font = pygame.font.Font(None, 64)
large_title_font = pygame.font.Font(None, 48)  # New font for selection screen titles
button_font = pygame.font.Font(None, 36)       # Increased from 32
subtitle_font = pygame.font.Font(None, 24)
small_font = pygame.font.Font(None, 20)

# Cell size - Reduced to fit better in window
cell_size = 45  # Reduced from size[0] // 10 (which was 60)

# Load space background
try:
    # Load first frame of GIF
    gif = Image.open("Resources/space.gif")
    frame = gif.convert('RGB')
    
    # Convert PIL image to pygame surface
    mode = frame.mode
    size_pil = frame.size
    data = frame.tobytes()
    
    space_bg = pygame.image.fromstring(data, size_pil, mode)
    space_bg = pygame.transform.scale(space_bg, size)
    print("GIF loaded successfully!")
except Exception as e:
    print(f"Error loading GIF: {e}")
    # If gif fails, create a starry background
    space_bg = pygame.Surface(size)
    space_bg.fill((5, 5, 25))
    import random
    for i in range(50):
        x = random.randint(0, size[0])
        y = random.randint(0, size[1])
        pygame.draw.circle(space_bg, WHITE, (x, y), 1)

# Load title image
try:
    title_img_original = pygame.image.load("Resources/title.png")
    # Get original dimensions
    original_width = title_img_original.get_width()
    original_height = title_img_original.get_height()
    
    # Scale to 80% of screen width while maintaining aspect ratio
    desired_width = int(size[0] * 0.8)  # 80% of screen width
    scale_factor = desired_width / original_width
    new_height = int(original_height * scale_factor)
    
    title_img = pygame.transform.scale(title_img_original, (desired_width, new_height))
except:
    title_img = None

# Load terrain images
terrain1_img = pygame.image.load("Resources/Terrain1.png")
terrain1_img = pygame.transform.scale(terrain1_img, (cell_size, cell_size))

terrain2_img = pygame.image.load("Resources/Terrain2.png")
terrain2_img = pygame.transform.scale(terrain2_img, (cell_size, cell_size))

terrain3_img = pygame.image.load("Resources/Terrain3.png")
terrain3_img = pygame.transform.scale(terrain3_img, (cell_size, cell_size))

terrain4_img = pygame.image.load("Resources/Terrain4.png")
terrain4_img = pygame.transform.scale(terrain4_img, (cell_size, cell_size))

# Load object images
sample_img = pygame.image.load("Resources/sample.png")
sample_img = pygame.transform.scale(sample_img, (cell_size, cell_size))

ship_img_original = pygame.image.load("Resources/ship.png")
ship_scale = 1.5
ship_size = int(cell_size * ship_scale)
ship_img = pygame.transform.scale(ship_img_original, (ship_size, ship_size))

# Load astronaut running animation sprites
astronaut_scale = 0.9  # Incrementar de 0.8 a 0.9 para mejor visibilidad
astronaut_size = int(cell_size * astronaut_scale)

# Load all 5 astronaut sprites
def scale_sprite_proportional(sprite_original, target_size):
    """Escala un sprite manteniendo sus proporciones originales y centrándolo"""
    original_width, original_height = sprite_original.get_size()
    
    # Calcular la escala para que quepa en el área objetivo manteniendo proporción
    scale_x = target_size / original_width
    scale_y = target_size / original_height
    scale = min(scale_x, scale_y)  # Usar la escala menor para mantener proporción
    
    # Nuevo tamaño manteniendo proporción
    new_width = int(original_width * scale)
    new_height = int(original_height * scale)
    
    # Escalar la imagen manteniendo proporción
    scaled_img = pygame.transform.scale(sprite_original, (new_width, new_height))
    
    # Crear una superficie del tamaño objetivo con fondo transparente
    final_surface = pygame.Surface((target_size, target_size), pygame.SRCALPHA)
    
    # Centrar la imagen escalada en la superficie final
    x_offset = (target_size - new_width) // 2
    y_offset = (target_size - new_height) // 2
    final_surface.blit(scaled_img, (x_offset, y_offset))
    
    return final_surface

astronaut_sprites = []
astronaut_sprites_flipped = []

for i in range(1, 6):  # Astronaut.png, Astronaut2.png, ..., Astronaut5.png
    if i == 1:
        filename = "Resources/Astronaut.png"
    else:
        filename = f"Resources/Astronaut{i}.png"
    
    try:
        # Load original sprite
        sprite_original = pygame.image.load(filename)
        
        # Escalar manteniendo proporciones originales
        sprite_scaled = scale_sprite_proportional(sprite_original, astronaut_size)
        astronaut_sprites.append(sprite_scaled)
        
        # Create flipped version for left movement
        sprite_flipped = pygame.transform.flip(sprite_scaled, True, False)  # Flip horizontally
        astronaut_sprites_flipped.append(sprite_flipped)
        
        print(f"Loaded astronaut sprite: {filename} - Size: {astronaut_size}x{astronaut_size} (proportional)")
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        # Fallback: use first sprite if others fail
        if astronaut_sprites:
            astronaut_sprites.append(astronaut_sprites[0])
            astronaut_sprites_flipped.append(astronaut_sprites_flipped[0])

# Fallback for compatibility (use first sprite)
astronaut_img = astronaut_sprites[0] if astronaut_sprites else None

# Load game screen specific images
try:
    space2_bg = pygame.image.load("Resources/space2.png")
    space2_bg = pygame.transform.scale(space2_bg, size)
    print("space2.png loaded successfully!")
except Exception as e:
    print(f"Error loading space2.png: {e}")
    space2_bg = space_bg  # Fallback to original space background

try:
    start_button_img = pygame.image.load("Resources/buttonstart.png")
    # Scale button to larger size
    button_width = 150  # Increased from 120
    button_height = 50   # Increased from 40
    start_button_img = pygame.transform.scale(start_button_img, (button_width, button_height))
    print("buttonstart.png loaded successfully!")
except Exception as e:
    print(f"Error loading buttonstart.png: {e}")
    start_button_img = None

def load_world_from_file():
    """Load world from text file using file dialog"""
    global world
    
    # Hide pygame window temporarily
    root = tk.Tk()
    root.withdraw()
    
    # Open file dialog
    file_path = filedialog.askopenfilename(
        title="Select World File",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    
    root.destroy()
    
    if file_path:
        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()
                new_world = []
                
                for line in lines:
                    # Skip empty lines and comment lines
                    line = line.strip()
                    if not line or line.startswith('//') or line.startswith('#'):
                        continue
                    
                    # Remove whitespace and split by spaces or commas
                    row_data = line.replace(',', ' ').split()
                    row = []
                    
                    for item in row_data:
                        try:
                            num = int(item)
                            row.append(num)
                        except ValueError:
                            # Skip non-numeric values
                            continue
                    
                    if len(row) == 10:  # Ensure we have exactly 10 columns
                        new_world.append(row)
                
                # Ensure we have exactly 10 rows
                if len(new_world) == 10:
                    world = new_world
                    print("World loaded successfully!")
                    return True
                else:
                    print(f"Error: World must be 10x10, but got {len(new_world)} rows")
                    return False
                    
        except Exception as e:
            print(f"Error loading file: {e}")
            return False
    
    return False

def draw_title_screen():
    """Draw the title screen"""
    # Draw space background
    screen.blit(space_bg, (0, 0))
    
    # Draw title with better positioning for larger screen
    if title_img:
        title_rect = title_img.get_rect(center=(size[0]//2, size[1]//3 - 20))
        screen.blit(title_img, title_rect)
    else:
        title_text = title_font.render("SMART ASTRONAUT", True, WHITE)
        title_rect = title_text.get_rect(center=(size[0]//2, size[1]//3 - 20))
        screen.blit(title_text, title_rect)
    
    # Draw subtitle with better spacing
    subtitle_text = subtitle_font.render("Misión de Exploración", True, GRAY)
    subtitle_rect = subtitle_text.get_rect(center=(size[0]//2, size[1]//3 + 60))
    screen.blit(subtitle_text, subtitle_rect)
    
    # Draw load file button with better positioning
    button_text = button_font.render("Cargar el mundo", True, WHITE)
    button_rect = pygame.Rect(size[0]//2 - 100, size[1]//2 + 100, 200, 50)
    pygame.draw.rect(screen, (50, 50, 100), button_rect)
    pygame.draw.rect(screen, WHITE, button_rect, 2)
    
    text_rect = button_text.get_rect(center=button_rect.center)
    screen.blit(button_text, text_rect)
    
    # Draw controls instructions
    controls_text = small_font.render("Presiona 'M' para pausar/reanudar música", True, GRAY)
    controls_rect = controls_text.get_rect(center=(size[0]//2, size[1] - 40))
    screen.blit(controls_text, controls_rect)
    
    return button_rect

def draw_algorithm_selection_screen():
    """Draw the algorithm type selection screen"""
    # Draw space background
    screen.blit(space_bg, (0, 0))
    
    # Draw title with better positioning for larger screen
    title_text = large_title_font.render("Selecciona tipo de búsqueda", True, WHITE)
    title_rect = title_text.get_rect(center=(size[0]//2, size[1]//6 + 20))
    screen.blit(title_text, title_rect)
    
    # Draw uninformed search button with more space
    uninformed_button_text = button_font.render("No Informada", True, WHITE)
    uninformed_button_rect = pygame.Rect(size[0]//2 - 100, size[1]//2 - 30, 200, 50)
    pygame.draw.rect(screen, (50, 100, 50), uninformed_button_rect)
    pygame.draw.rect(screen, WHITE, uninformed_button_rect, 2)
    
    uninformed_text_rect = uninformed_button_text.get_rect(center=uninformed_button_rect.center)
    screen.blit(uninformed_button_text, uninformed_text_rect)
    
    # Draw informed search button with better spacing
    informed_button_text = button_font.render("Informada", True, WHITE)
    informed_button_rect = pygame.Rect(size[0]//2 - 100, size[1]//2 + 40, 200, 50)
    pygame.draw.rect(screen, (100, 50, 100), informed_button_rect)
    pygame.draw.rect(screen, WHITE, informed_button_rect, 2)
    
    informed_text_rect = informed_button_text.get_rect(center=informed_button_rect.center)
    screen.blit(informed_button_text, informed_text_rect)
    
    # Back button
    back_button_text = subtitle_font.render("Atrás", True, WHITE)
    back_button_rect = pygame.Rect(20, size[1] - 50, 80, 30)
    pygame.draw.rect(screen, (100, 100, 100), back_button_rect)
    pygame.draw.rect(screen, WHITE, back_button_rect, 2)
    
    back_text_rect = back_button_text.get_rect(center=back_button_rect.center)
    screen.blit(back_button_text, back_text_rect)
    
    return uninformed_button_rect, informed_button_rect, back_button_rect

def draw_uninformed_selection_screen():
    """Draw the uninformed algorithm selection screen"""
    # Draw space background
    screen.blit(space_bg, (0, 0))
    
    # Draw title with larger font
    title_text = large_title_font.render("Búsqueda No Informada", True, WHITE)
    title_rect = title_text.get_rect(center=(size[0]//2, size[1]//8))
    screen.blit(title_text, title_rect)
    
    # Draw algorithm buttons with smaller text and buttons
    algorithms = [
        ("Amplitud", "breadth"),
        ("Costo Uniforme", "uniform_cost"),
        ("Profundidad", "depth")
    ]
    
    button_rects = []
    for i, (display_name, algorithm_name) in enumerate(algorithms):
        button_text = subtitle_font.render(display_name, True, WHITE)
        button_rect = pygame.Rect(size[0]//2 - 120, size[1]//3 + i * 60, 240, 45)
        pygame.draw.rect(screen, (50, 50, 150), button_rect)
        pygame.draw.rect(screen, WHITE, button_rect, 2)
        
        text_rect = button_text.get_rect(center=button_rect.center)
        screen.blit(button_text, text_rect)
        
        button_rects.append((button_rect, algorithm_name))
    
    # Back button
    back_button_text = subtitle_font.render("Atrás", True, WHITE)
    back_button_rect = pygame.Rect(20, size[1] - 50, 80, 30)
    pygame.draw.rect(screen, (100, 100, 100), back_button_rect)
    pygame.draw.rect(screen, WHITE, back_button_rect, 2)
    
    back_text_rect = back_button_text.get_rect(center=back_button_rect.center)
    screen.blit(back_button_text, back_text_rect)
    
    return button_rects, back_button_rect

def draw_informed_selection_screen():
    """Draw the informed algorithm selection screen"""
    # Draw space background
    screen.blit(space_bg, (0, 0))
    
    # Draw title with larger font
    title_text = large_title_font.render("Búsqueda Informada", True, WHITE)
    title_rect = title_text.get_rect(center=(size[0]//2, size[1]//8))
    screen.blit(title_text, title_rect)
    
    # Draw algorithm buttons
    algorithms = [
        ("Avara", "greedy"),
        ("A*", "a_star")
    ]
    
    button_rects = []
    for i, (display_name, algorithm_name) in enumerate(algorithms):
        button_text = button_font.render(display_name, True, WHITE)
        button_rect = pygame.Rect(size[0]//2 - 100, size[1]//3 + i * 80, 200, 50)
        pygame.draw.rect(screen, (150, 50, 50), button_rect)
        pygame.draw.rect(screen, WHITE, button_rect, 2)
        
        text_rect = button_text.get_rect(center=button_rect.center)
        screen.blit(button_text, text_rect)
        
        button_rects.append((button_rect, algorithm_name))
    
    # Back button
    back_button_text = subtitle_font.render("Atrás", True, WHITE)
    back_button_rect = pygame.Rect(20, size[1] - 50, 80, 30)
    pygame.draw.rect(screen, (100, 100, 100), back_button_rect)
    pygame.draw.rect(screen, WHITE, back_button_rect, 2)
    
    back_text_rect = back_button_text.get_rect(center=back_button_rect.center)
    screen.blit(back_button_text, back_text_rect)
    
    return button_rects, back_button_rect

def draw_game_screen():
    """Draw the game world with improved design using specific assets"""
    # Draw space2 background
    screen.blit(space2_bg, (0, 0))
    
    # Draw title image instead of text - positioned to be fully visible
    if title_img:
        # Scale title larger to be more visible
        title_scale = 0.7  # Increased from 0.5
        title_width = int(title_img.get_width() * title_scale)
        title_height = int(title_img.get_height() * title_scale)
        title_scaled = pygame.transform.scale(title_img, (title_width, title_height))
        title_rect = title_scaled.get_rect(center=(size[0]//2, 85))  # Moved from 65 to 85 for better margin
        screen.blit(title_scaled, title_rect)
    else:
        # Fallback to text if image fails
        title_text = large_title_font.render("SMART ASTRONAUT", True, WHITE)
        title_rect = title_text.get_rect(center=(size[0]//2, 85))  # Moved from 65 to 85 for better margin
        screen.blit(title_text, title_rect)
    
    # Draw selected algorithm info - positioned BELOW the title
    if selected_algorithm:
        algo_text = subtitle_font.render(f"Algoritmo: {selected_algorithm}", True, WHITE)
        algo_rect = algo_text.get_rect(center=(size[0]//2, 135))  # Moved from 125 to 135 for more spacing
        screen.blit(algo_text, algo_rect)
    
    # Calculate grid position to center it with more spacing from title/algorithm
    grid_size = cell_size * 10  # Grid is now 450x450 instead of 600x600
    grid_x = (size[0] - grid_size) // 2
    grid_y = 155  # Moved from 145 to 155 to accommodate algorithm text below title
    
    # Draw the grid
    for row in range(10):
        for col in range(10):
            x = grid_x + col * cell_size
            y = grid_y + row * cell_size

            value = world[row][col]

            # Draw texture or color depending on value
            if value == 0:   # Free
                screen.blit(terrain1_img, (x, y))
            elif value == 1: # Obstacle
                screen.blit(terrain4_img, (x, y))
            elif value == 3: # Rocky
                screen.blit(terrain2_img, (x, y))
            elif value == 4: # Volcanic
                screen.blit(terrain3_img, (x, y))
            elif value == 6: # Sample (object on top of terrain1)
                screen.blit(terrain1_img, (x, y))
                screen.blit(sample_img, (x, y))
            elif value == 5: # Ship (object on top of terrain1, larger and centered)
                screen.blit(terrain1_img, (x, y))
                # Center the larger ship image in the cell
                ship_offset = (ship_size - cell_size) // 2
                screen.blit(ship_img, (x - ship_offset, y - ship_offset))
            elif value == 2: # Astronaut (object on top of terrain1, centered)
                screen.blit(terrain1_img, (x, y))
                astronaut_offset = (astronaut_size - cell_size) // 2
                current_astronaut_sprite = get_astronaut_sprite()
                screen.blit(current_astronaut_sprite, (x - astronaut_offset, y - astronaut_offset))
            
            # Draw borders for all cells with BLACK color
            pygame.draw.rect(screen, BLACK, (x, y, cell_size, cell_size), 1)
    
    # Draw START button - positioned to be clearly visible and larger
    button_y = grid_y + grid_size + 20  # 20px space from grid
    start_button_rect = pygame.Rect(size[0]//2 - 75, button_y, 150, 50)  # Increased from 120x40 to 150x50
    
    if start_button_img:
        # Scale the button image to the new size
        start_button_scaled = pygame.transform.scale(start_button_img, (150, 50))
        screen.blit(start_button_scaled, start_button_rect)
    else:
        # Fallback to drawn button with larger size
        start_button_text = button_font.render("START", True, WHITE)
        pygame.draw.rect(screen, (100, 50, 150), start_button_rect)
        pygame.draw.rect(screen, WHITE, start_button_rect, 2)
        
        start_text_rect = start_button_text.get_rect(center=start_button_rect.center)
        screen.blit(start_button_text, start_text_rect)
    
    # Back button - positioned at bottom
    back_button_text = subtitle_font.render("Atrás", True, WHITE)
    back_button_rect = pygame.Rect(20, size[1] - 50, 80, 30)
    pygame.draw.rect(screen, (100, 100, 100), back_button_rect)
    pygame.draw.rect(screen, WHITE, back_button_rect, 2)
    
    back_text_rect = back_button_text.get_rect(center=back_button_rect.center)
    screen.blit(back_button_text, back_text_rect)
    
    return start_button_rect, back_button_rect

def get_astronaut_sprite():
    """Obtiene el sprite actual del astronauta basado en la dirección y animación"""
    global current_sprite_index, astronaut_direction, is_animating
    
    if not astronaut_sprites:
        return astronaut_img  # Fallback
    
    # Si no está animando (parado), usar el sprite 1 (índice 0)
    if not is_animating:
        if astronaut_direction == "left":
            return astronaut_sprites_flipped[0]
        else:
            return astronaut_sprites[0]
    
    # Para animación de caminar, usar sprites 2-5 (índices 1-4)
    # Mapear current_sprite_index (0-3) a sprites de caminar (1-4)
    walking_sprite_index = (current_sprite_index % 4) + 1
    
    # Devolver sprite según la dirección
    if astronaut_direction == "left":
        return astronaut_sprites_flipped[walking_sprite_index]
    else:
        return astronaut_sprites[walking_sprite_index]

def update_astronaut_direction(old_pos, new_pos):
    """Actualiza la dirección del astronauta basado en el movimiento"""
    global astronaut_direction, current_sprite_index
    
    old_col, new_col = old_pos[1], new_pos[1]
    
    # Determinar dirección horizontal
    if new_col < old_col:
        astronaut_direction = "left"
    elif new_col > old_col:
        astronaut_direction = "right"
    # Si solo se mueve verticalmente, mantener la dirección actual
    
    # Avanzar al siguiente sprite de la animación
    current_sprite_index = (current_sprite_index + 1) % len(astronaut_sprites)

def update_animation():
    """Actualiza la animación del astronauta moviéndose por el camino"""
    global current_step, animation_counter, astronaut_pos, is_animating, collected_samples, world
    global current_cost, has_ship, fuel_left, animation_completed
    
    # Si no está animando o ya completó, no hacer nada
    if not is_animating or animation_completed:
        return
    
    animation_counter += 1
    
    # Controlar velocidad de animación
    if animation_counter >= animation_speed:
        animation_counter = 0
        
        # Mover astronauta al siguiente paso
        if current_step < len(algorithm_path):
            # Nueva posición (NO modificar el mundo, solo la posición del astronauta)
            new_pos = algorithm_path[current_step]
            
            # Actualizar dirección y sprite del astronauta antes de moverlo
            if current_step > 0:  # Solo si no es el primer paso
                update_astronaut_direction(astronaut_pos, new_pos)
            
            astronaut_pos = new_pos
            new_row, new_col = new_pos
            
            # Solo calcular costo si no es el primer paso (posición inicial no cuesta)
            if current_step > 0:
                # Verificar si llega a la nave (usando mundo original)
                if original_world[new_row][new_col] == 5 and not has_ship:
                    has_ship = True
                    fuel_left = 20
                    print(f"¡Astronauta subió a la nave! Combustible: {fuel_left}")
                    # Reproducir sonido de nave
                    if ship_sound:
                        ship_sound.play()
                
                # Actualizar combustible si tiene nave
                if has_ship and fuel_left > 0:
                    fuel_left -= 1
                
                # Calcular costo del movimiento usando el terreno original
                terrain_type = original_world[new_row][new_col]
                step_cost = calcular_costo_movimiento(terrain_type, has_ship, fuel_left >= 0)
                current_cost += step_cost
                
                # Mostrar información del paso
                terrain_names = {0: "Libre", 3: "Rocoso", 4: "Volcánico", 5: "Nave", 6: "Muestra"}
                terrain_name = terrain_names.get(terrain_type, "Libre")
                cost_info = f"(+{step_cost})" if not (has_ship and fuel_left >= 0) else f"(+{step_cost} con nave)"
                print(f"Paso {current_step}: {terrain_name} {cost_info} | Costo total: {current_cost}")
            
            # Verificar si recoge una muestra (usando mundo original)
            if original_world[new_row][new_col] == 6:  # Muestra
                collected_samples.add(new_pos)
                print(f"¡Muestra recolectada en {new_pos}! Total: {len(collected_samples)}")
                # Reproducir sonido de muestra recolectada
                if sample_sound:
                    sample_sound.play()
            
            current_step += 1
            
            # Verificar si terminó
            if current_step >= len(algorithm_path):
                # NO cambiar is_animating a False para mantener visible el astronauta y camino
                animation_completed = True  # Marcar como completada para mantener el estado final
                current_sprite_index = 0  # Resetear a sprite de parado (sprite 1)
                print("¡Animación completada!")
                print(f"Costo final: {current_cost}")
                print(f"Muestras recolectadas: {len(collected_samples)}")

def draw_simulation_screen():
    """Dibuja la pantalla de simulación con la animación en progreso"""
    global is_animating, animation_completed, astronaut_pos, current_step, algorithm_path
    
    # Draw space2 background
    screen.blit(space2_bg, (0, 0))
    
    # Draw title
    if title_img:
        title_scale = 0.5
        title_width = int(title_img.get_width() * title_scale)
        title_height = int(title_img.get_height() * title_scale)
        title_scaled = pygame.transform.scale(title_img, (title_width, title_height))
        title_rect = title_scaled.get_rect(center=(size[0]//2, 50))
        screen.blit(title_scaled, title_rect)
    
    # Draw algorithm info
    if algorithm_result:
        algo_text = subtitle_font.render(f"Algoritmo: {algorithm_result['algorithm']}", True, WHITE)
        algo_rect = algo_text.get_rect(center=(size[0]//2, 80))
        screen.blit(algo_text, algo_rect)
        
        # Draw progress info con costo actual
        if animation_completed:
            progress_text = small_font.render(f"¡COMPLETADO! | Pasos: {len(algorithm_path)-1} | Costo Final: {current_cost}", True, GREEN)
        else:
            progress_text = small_font.render(f"Paso: {current_step}/{len(algorithm_path)} | Costo: {current_cost}", True, WHITE)
        progress_rect = progress_text.get_rect(center=(size[0]//2, 100))
        screen.blit(progress_text, progress_rect)
        
        # Draw samples collected
        samples_text = small_font.render(f"Muestras recolectadas: {len(collected_samples)}", True, GREEN)
        samples_rect = samples_text.get_rect(center=(size[0]//2, 120))
        screen.blit(samples_text, samples_rect)
        
        # Draw ship info if applicable
        if has_ship:
            ship_text = small_font.render(f"🚀 Nave: Combustible {fuel_left}/20", True, YELLOW)
            ship_rect = ship_text.get_rect(center=(size[0]//2, 140))
            screen.blit(ship_text, ship_rect)
            grid_y = 160  # Adjust grid position
        else:
            grid_y = 140
    
    # Calculate grid position (will be overridden above)
    grid_size = cell_size * 10
    grid_x = (size[0] - grid_size) // 2
    
    # Draw the grid with animation usando el mundo original
    for row in range(10):
        for col in range(10):
            x = grid_x + col * cell_size
            y = grid_y + row * cell_size
            
            # Usar el valor del mundo original para preservar los terrenos
            value = original_world[row][col] if original_world else world[row][col]
            
            # Draw texture or color depending on value
            if value == 0:   # Free
                screen.blit(terrain1_img, (x, y))
            elif value == 1: # Obstacle
                screen.blit(terrain4_img, (x, y))
            elif value == 3: # Rocky
                screen.blit(terrain2_img, (x, y))
            elif value == 4: # Volcanic
                screen.blit(terrain3_img, (x, y))
            elif value == 6: # Sample (only if not collected)
                screen.blit(terrain1_img, (x, y))
                if (row, col) not in collected_samples:
                    screen.blit(sample_img, (x, y))
            elif value == 5: # Ship
                screen.blit(terrain1_img, (x, y))
                ship_offset = (ship_size - cell_size) // 2
                screen.blit(ship_img, (x - ship_offset, y - ship_offset))
            elif value == 2: # Astronaut position (draw as free terrain)
                screen.blit(terrain1_img, (x, y))
            
            # Draw astronaut on top if this is his current position (durante animación o cuando terminó)
            if (row, col) == astronaut_pos and (is_animating or animation_completed):
                astronaut_offset = (astronaut_size - cell_size) // 2
                current_astronaut_sprite = get_astronaut_sprite()
                screen.blit(current_astronaut_sprite, (x - astronaut_offset, y - astronaut_offset))
            
            # Draw borders
            pygame.draw.rect(screen, BLACK, (x, y, cell_size, cell_size), 1)
            
            # Highlight path - mostrar camino completo si la animación terminó, o solo hasta el paso actual
            if animation_completed:
                # Si terminó, mostrar todo el camino excepto donde está el astronauta
                if (row, col) in algorithm_path and (row, col) != astronaut_pos:
                    pygame.draw.rect(screen, YELLOW, (x, y, cell_size, cell_size), 3)
            else:
                # Durante la animación, mostrar solo hasta el paso actual
                if current_step < len(algorithm_path) and (row, col) in algorithm_path[:current_step]:
                    if (row, col) != astronaut_pos:  # No highlight current astronaut position
                        pygame.draw.rect(screen, YELLOW, (x, y, cell_size, cell_size), 3)
    
    # Draw buttons
    button_y = grid_y + grid_size + 20
    
    # Reset button
    reset_text = subtitle_font.render("Reiniciar", True, WHITE)
    reset_button_rect = pygame.Rect(size[0]//2 - 100, button_y, 80, 30)
    pygame.draw.rect(screen, (100, 50, 50), reset_button_rect)
    pygame.draw.rect(screen, WHITE, reset_button_rect, 2)
    
    reset_text_rect = reset_text.get_rect(center=reset_button_rect.center)
    screen.blit(reset_text, reset_text_rect)
    
    # Back button
    back_text = subtitle_font.render("Atrás", True, WHITE)
    back_button_rect = pygame.Rect(size[0]//2 + 20, button_y, 80, 30)
    pygame.draw.rect(screen, (100, 100, 100), back_button_rect)
    pygame.draw.rect(screen, WHITE, back_button_rect, 2)
    
    back_text_rect = back_text.get_rect(center=back_button_rect.center)
    screen.blit(back_text, back_text_rect)
    
    return reset_button_rect, back_button_rect

def toggle_music():
    """Función para pausar/reanudar la música de fondo"""
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.pause()
        print("Música pausada")
    else:
        pygame.mixer.music.unpause()
        print("Música reanudada")

# Main game loop
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            if current_state == TITLE_SCREEN:
                load_button = draw_title_screen()
                
                if load_button.collidepoint(mouse_pos):
                    # Load world from file
                    if load_world_from_file():
                        current_state = SELECT_ALGORITHM_SCREEN
            
            elif current_state == SELECT_ALGORITHM_SCREEN:
                uninformed_button, informed_button, back_button = draw_algorithm_selection_screen()
                
                if uninformed_button.collidepoint(mouse_pos):
                    selected_algorithm_type = "uninformed"
                    current_state = SELECT_UNINFORMED_SCREEN
                
                elif informed_button.collidepoint(mouse_pos):
                    selected_algorithm_type = "informed"
                    current_state = SELECT_INFORMED_SCREEN
                
                elif back_button.collidepoint(mouse_pos):
                    current_state = TITLE_SCREEN
            
            elif current_state == SELECT_UNINFORMED_SCREEN:
                algorithm_buttons, back_button = draw_uninformed_selection_screen()
                
                for button_rect, algorithm_name in algorithm_buttons:
                    if button_rect.collidepoint(mouse_pos):
                        selected_algorithm = algorithm_name
                        print(f"Selected algorithm: {algorithm_name}")
                        current_state = GAME_SCREEN
                        break
                
                if back_button.collidepoint(mouse_pos):
                    current_state = SELECT_ALGORITHM_SCREEN
            
            elif current_state == SELECT_INFORMED_SCREEN:
                algorithm_buttons, back_button = draw_informed_selection_screen()
                
                for button_rect, algorithm_name in algorithm_buttons:
                    if button_rect.collidepoint(mouse_pos):
                        selected_algorithm = algorithm_name
                        print(f"Selected algorithm: {algorithm_name}")
                        current_state = GAME_SCREEN
                        break
                
                if back_button.collidepoint(mouse_pos):
                    current_state = SELECT_ALGORITHM_SCREEN
            
            elif current_state == GAME_SCREEN:
                start_button, back_button = draw_game_screen()
                
                if start_button.collidepoint(mouse_pos):
                    if selected_algorithm == "breadth":
                        # Ejecutar búsqueda por amplitud
                        print(f"Ejecutando algoritmo: {selected_algorithm}")
                        result = ejecutar_busqueda_amplitud(world)
                        
                        if result and result.get("success"):
                            # Guardar copia del mundo original
                            original_world = [row[:] for row in world]  # Copia profunda
                            
                            algorithm_path = result["path"]
                            algorithm_result = result
                            current_step = 0
                            collected_samples = set()
                            is_animating = True
                            current_cost = 0  # Inicializar costo en 0
                            has_ship = False  # Inicializar sin nave
                            fuel_left = 0     # Sin combustible inicialmente
                            current_sprite_index = 0  # Resetear animación de sprites
                            astronaut_direction = "right"  # Dirección inicial
                            animation_completed = False  # Resetear estado de animación
                            
                            # Encontrar posición inicial del astronauta
                            for row in range(10):
                                for col in range(10):
                                    if world[row][col] == 2:
                                        astronaut_pos = (row, col)
                                        break
                            
                            print(f"Camino encontrado: {len(algorithm_path)} pasos")
                            print(f"Costo total: {result['total_cost']}")
                            current_state = SIMULATION_SCREEN
                        else:
                            error_msg = result.get("error", "Error desconocido")
                            print(f"Error: {error_msg}")
                    if selected_algorithm == "greedy":
                        # Ejecutar búsqueda voraz
                        print(f"Ejecutando algoritmo: {selected_algorithm}")
                        result = greedy_search(world)
                        
                        if result and result.get("success"):
                            # Guardar copia del mundo original
                            original_world = [row[:] for row in world]  # Copia profunda
                            
                            algorithm_path = result["path"]
                            algorithm_result = result
                            current_step = 0
                            collected_samples = set()
                            is_animating = True
                            current_cost = 0  # Inicializar costo en 0
                            has_ship = False  # Inicializar sin nave
                            fuel_left = 0     # Sin combustible inicialmente
                            current_sprite_index = 0  # Resetear animación de sprites
                            astronaut_direction = "right"  # Dirección inicial
                            animation_completed = False  # Resetear estado de animación
                            
                            # Encontrar posición inicial del astronauta
                            for row in range(10):
                                for col in range(10):
                                    if world[row][col] == 2:
                                        astronaut_pos = (row, col)
                                        break
                            
                            print(f"Camino encontrado: {len(algorithm_path)} pasos")
                            print(f"Costo total: {result['total_cost']}")
                            current_state = SIMULATION_SCREEN
                    if selected_algorithm == "a_star":
                        print(f"Ejecutando algoritmo: {selected_algorithm}")
                        result = a_star(world)
                            
                        if result and result.get("success"):
                            # Guardar copia del mundo original
                            original_world = [row[:] for row in world]  # Copia profunda
                                
                            algorithm_path = result["path"]
                            algorithm_result = result
                            current_step = 0
                            collected_samples = set()
                            is_animating = True
                            current_cost = 0  # Inicializar costo en 0
                            has_ship = False  # Inicializar sin nave
                            fuel_left = 0     # Sin combustible inicialmente
                            current_sprite_index = 0  # Resetear animación de sprites
                            astronaut_direction = "right"  # Dirección inicial
                            animation_completed = False  # Resetear estado de animación
                                
                                # Encontrar posición inicial del astronauta
                            for row in range(10):
                                for col in range(10):
                                    if world[row][col] == 2:
                                        astronaut_pos = (row, col)
                                        break
                                
                            print(f"Camino encontrado: {len(algorithm_path)} pasos")
                            print(f"Costo total: {result['total_cost']}")
                            current_state = SIMULATION_SCREEN    
                        else:
                            error_msg = result.get("error", "Error desconocido")
                            print(f"Error: {error_msg}")
                    else:
                        print(f"Algoritmo {selected_algorithm} aún no implementado")
                
                elif back_button.collidepoint(mouse_pos):
                    current_state = SELECT_ALGORITHM_SCREEN
            
            elif current_state == SIMULATION_SCREEN:
                reset_button, back_button = draw_simulation_screen()
                
                if reset_button.collidepoint(mouse_pos):
                    # Reiniciar la simulación
                    current_step = 0
                    animation_counter = 0
                    is_animating = True
                    collected_samples = set()
                    current_cost = 0      # Resetear costo a 0
                    has_ship = False      # Resetear nave
                    fuel_left = 0         # Resetear combustible
                    current_sprite_index = 0  # Resetear animación de sprites
                    astronaut_direction = "right"  # Dirección inicial
                    animation_completed = False  # Resetear estado completado
                    
                    # Restaurar el mundo completamente desde la copia original
                    if original_world:
                        for row in range(10):
                            for col in range(10):
                                world[row][col] = original_world[row][col]
                    
                    # Establecer posición inicial del astronauta
                    if algorithm_path:
                        start_pos = algorithm_path[0]
                        astronaut_pos = start_pos
                
                elif back_button.collidepoint(mouse_pos):
                    current_state = GAME_SCREEN
                    # Reset animation state and restore world
                    is_animating = False
                    current_step = 0
                    collected_samples = set()
                    current_cost = 0
                    has_ship = False
                    fuel_left = 0
                    animation_completed = False
                    current_sprite_index = 0
                    astronaut_direction = "right"
                    
                    # Restaurar mundo original
                    if original_world:
                        for row in range(10):
                            for col in range(10):
                                world[row][col] = original_world[row][col]
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if current_state == GAME_SCREEN:
                    current_state = TITLE_SCREEN
                elif current_state == SIMULATION_SCREEN:
                    current_state = GAME_SCREEN
                    is_animating = False
                    current_step = 0
                    collected_samples = set()
                    current_cost = 0
                    has_ship = False
                    fuel_left = 0
                    animation_completed = False
                    current_sprite_index = 0
                    astronaut_direction = "right"
                    
                    # Restaurar mundo original
                    if original_world:
                        for row in range(10):
                            for col in range(10):
                                world[row][col] = original_world[row][col]
                elif current_state in [SELECT_ALGORITHM_SCREEN, SELECT_UNINFORMED_SCREEN, SELECT_INFORMED_SCREEN]:
                    current_state = TITLE_SCREEN
            elif event.key == pygame.K_m:
                # Tecla M para pausar/reanudar música
                toggle_music()
    
    # Update animation if in simulation mode
    if current_state == SIMULATION_SCREEN and is_animating:
        update_animation()
    
    # Draw based on current state
    if current_state == TITLE_SCREEN:
        draw_title_screen()
    elif current_state == SELECT_ALGORITHM_SCREEN:
        draw_algorithm_selection_screen()
    elif current_state == SELECT_UNINFORMED_SCREEN:
        draw_uninformed_selection_screen()
    elif current_state == SELECT_INFORMED_SCREEN:
        draw_informed_selection_screen()
    elif current_state == GAME_SCREEN:
        draw_game_screen()
    elif current_state == SIMULATION_SCREEN:
        draw_simulation_screen()
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()