# Smart Astronaut

Proyecto educativo de búsqueda y planificación para un agente (astronauta) que debe recolectar muestras en un mapa 10x10. Incluye varias implementaciones de algoritmos de búsqueda (BFS, DFS, A*, Greedy, Uniform Cost) y una interfaz visual en Pygame que anima la solución encontrada.

## Contenido del repositorio

- `main.py` — Programa principal y UI (Pygame). Desde aquí se carga el mundo, se seleccionan algoritmos, se lanza la búsqueda y se anima el recorrido paso a paso. También muestra un informe con métricas (costo de la solución, tiempo de cómputo, nodos expandidos, etc.).

- `world_example.txt`, `world_example2.txt` — Ejemplos de mundos (mapas) en formato de texto que `main.py` puede cargar.

- `Algorithms/` — Carpeta con las implementaciones de búsqueda y utilidades:
  - `a_star.py` — Implementación del algoritmo A* adaptado al problema (maneja estado de nave/combustible y recolección de muestras).
  - `breadth.py` — Implementación de búsqueda por amplitud (BFS). También contiene utilidades usadas por otros algoritmos:
    - `search_path(...)` — motor interno de BFS que devuelve camino y costo acumulado.
    - `calculate_movement_cost(...)` — calcula el costo de moverse a una casilla según el terreno y si el agente tiene nave y combustible.
    - `find_special_positions(...)` — detecta la posición inicial del astronauta, la nave y las muestras en el mundo.
    - `execute_breadth_search(...)` — función pública que ejecuta la búsqueda por amplitud y devuelve un diccionario con `path`, `total_cost` y métricas.
  - `depth.py` — Búsqueda en profundidad (DFS). Usa la misma convención de estado que BFS.
  - `greedy.py` — Búsqueda voraz / greedy (heurística). Implementación propia adaptada al dominio.
  - `uniform_cost.py` — Búsqueda de costo uniforme (Dijkstra-like) para obtener caminos óptimos por costo.
  - `complement.py` — Funciones auxiliares (heurísticas, reconstrucción de camino, costos base por terreno, etc.).
  - `objects.py` — Definición de la clase `Node` usada por algoritmos informados.

- `Resources/` — Imágenes y assets (sprites, fondos, botones, tiles).
- `Sounds/` — Efectos y música del juego.

## Estructura del mundo (mapa)
Cada mundo es una matriz 10x10 con valores numéricos que representan:
- `0` — terreno libre (costo 1)
- `1` — obstáculo (no transitable)
- `2` — posición inicial del astronauta
- `3` — terreno rocoso (costo 3)
- `4` — terreno volcánico (costo 5)
- `5` — nave (al subir da combustible y reduce costo en movimientos siguientes)
- `6` — muestra científica (objetivo a recolectar)

Las implementaciones consideran el estado del agente: posiciones recolectadas, si tiene la nave y cuántas unidades de combustible le quedan.

## Dependencias
El proyecto usa Python 3.10+ y estas librerías principales:
- pygame
- pillow (PIL)

Instalación rápida (recomendada dentro de un virtual environment):

Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install pygame pillow
```

## Cómo ejecutar
Desde la raíz del proyecto (donde está `main.py`) activar el virtualenv (si usas uno) y ejecuta:

Windows PowerShell

```powershell
python main.py
```

La interfaz abrirá una ventana. Pasos básicos en la UI:
1. Cargar un mundo (opcional): botón "Cargar el mundo" y seleccionar `world_example.txt` o tu propio archivo.
2. Seleccionar tipo de búsqueda (informada/no informada) y elegir un algoritmo.
3. Iniciar la búsqueda. Si encuentra solución, se abrirá la pantalla de simulación y se reproducirá la animación del camino encontrado.
4. Al completar la animación puedes pulsar "Ver informe" para ver métricas como `Costo solución`, `Tiempo de cómputo`, `Nodos expandidos`, etc.

## Notas sobre reproducibilidad y valores de costo
- Los algoritmos devuelven un `path` (lista de coordenadas) y un `total_cost`. La UI usa esa información para animar el camino y calcular el costo real paso a paso considerando el estado previo (boarding/no boarding, consumo de combustible). Si ves discrepancias entre lo que el algoritmo devuelve y lo que la animación muestra, revisa la lógica que normaliza el `path` (la UI espera que el primer elemento del `path` sea la posición inicial).

## Sugerencias y pruebas
- Para probar con distintos mundos crear archivos `.txt` con 10 líneas de 10 números separados por espacios.
- Para debug visual agregar `print(...)` en los algoritmos (ellos ya imprimen algunas trazas por consola como "Camino encontrado" y desglose de costos).

## Licencia y créditos
Proyecto académico creado por Dylan F. Morales R. y Johan A. Ceballos T. (Universidad del Valle). Usa assets locales en `Resources/` y `Sounds/`.

## Agradecimientos

Se agradece especialmente a los proveedores de sonido para la ambientación del juego:

- http://www.universalrsoundbank.com/ — por los efectos de sonido utilizados en este proyecto.
- Pixel Worlds — por la música de fondo tomada para las interacciones del juego.

## Enlace de GitHub
https://github.com/JohanAndresCT/smartastronaut
