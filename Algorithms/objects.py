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
# Archivo: objects.py
# --------------------------------------------------------

class Node:
    def __init__(self, state, parent=None, h=None, action=None,hPost=None,f=None,
                 path_cost=0, rocket=False, rocketFuel=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost
        self.h = h
        self.f = f
        self.hPost = hPost
        self.children = []
        self.rocket = rocket
        self.rocketFuel = rocketFuel

    def __repr__(self):
        return f"Node(state={self.state}, g={self.path_cost}, h={self.h}, action={self.action}, rocket={self.rocket}, fuel={self.rocketFuel})"

    def f(self):
        return self.path_cost + self.h