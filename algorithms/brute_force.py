"""
Implementação do algoritmo Par de Pontos Mais Próximos via Força Bruta.

Complexidade: O(n²), onde n = |points_a| + |points_b|.
Avalia todos os n*(n-1)/2 pares do conjunto unificado.
Usado como baseline de corretude para validar o Dividir e Conquistar.
"""

import time

from algorithms.utils import euclidean_distance


def brute_force_closest(points_a, points_b):
    """
    Encontra o par mais próximo no conjunto unificado points_a + points_b.

    Avalia todos os n*(n-1)/2 pares — mesma semântica do Dividir e Conquistar,
    permitindo comparação direta de corretude e desempenho.

    Retorna dict com:
        pair        – tupla (p1, p2) com os pontos mais próximos
        distance    – distância euclidiana entre eles
        comparisons – número total de pares avaliados
        time_ms     – tempo de execução em milissegundos
    """
    all_points = points_a + points_b
    if len(all_points) < 2:
        raise ValueError("São necessários ao menos 2 pontos no total.")

    best_pair = None
    best_dist = float("inf")
    comparisons = 0

    start = time.perf_counter()

    for i in range(len(all_points)):
        for j in range(i + 1, len(all_points)):
            dist = euclidean_distance(all_points[i], all_points[j])
            comparisons += 1
            if dist < best_dist:
                best_dist = dist
                best_pair = (all_points[i], all_points[j])

    elapsed_ms = (time.perf_counter() - start) * 1000

    return {
        "pair": best_pair,
        "distance": best_dist,
        "comparisons": comparisons,
        "time_ms": elapsed_ms,
    }
