"""
Implementação do algoritmo Par de Pontos Mais Próximos via Força Bruta.

Complexidade: O(n * m), onde n = |points_a| e m = |points_b|.
Usado como baseline de corretude para validar o Dividir e Conquistar.
"""

import math
import time


def euclidean_distance(p1, p2):
    """Distância euclidiana entre dois pontos com campos 'x' e 'y'."""
    return math.sqrt((p1["x"] - p2["x"]) ** 2 + (p1["y"] - p2["y"]) ** 2)


def brute_force_closest(points_a, points_b):
    """
    Encontra o par mais próximo entre points_a e points_b por força bruta.

    Itera todos os pares (a, b) com a ∈ points_a e b ∈ points_b.

    Retorna dict com:
        pair        – tupla (p1, p2) com os pontos mais próximos
        distance    – distância euclidiana entre eles
        comparisons – número total de pares avaliados
        time_ms     – tempo de execução em milissegundos
    """
    if not points_a or not points_b:
        raise ValueError("Ambas as listas devem conter ao menos um ponto.")

    best_pair = None
    best_dist = math.inf
    comparisons = 0

    start = time.perf_counter()

    for a in points_a:
        for b in points_b:
            dist = euclidean_distance(a, b)
            comparisons += 1
            if dist < best_dist:
                best_dist = dist
                best_pair = (a, b)

    elapsed_ms = (time.perf_counter() - start) * 1000

    return {
        "pair": best_pair,
        "distance": best_dist,
        "comparisons": comparisons,
        "time_ms": elapsed_ms,
    }
