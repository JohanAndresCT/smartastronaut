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