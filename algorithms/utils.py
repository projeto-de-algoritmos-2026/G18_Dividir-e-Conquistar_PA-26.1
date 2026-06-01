"""
Utilitários compartilhados pelos módulos de algoritmo.
"""

import math


def euclidean_distance(p1, p2):
    """Distância euclidiana entre dois pontos com campos 'x' e 'y'."""
    return math.hypot(p1["x"] - p2["x"], p1["y"] - p2["y"])
