"""
Implementação do algoritmo Par de Pontos Mais Próximos via Dividir e Conquistar.

Complexidade: O(n log n), onde n = |points_a| + |points_b|.
A faixa central (strip) garante que no máximo 7 vizinhos precisam ser checados
por ponto, mantendo o passo de combinação em O(n).
"""

import math
import time

from algorithms.utils import euclidean_distance

# Registra steps de animação apenas nos primeiros N+1 níveis da recursão (0-indexado).
_ANIM_MAX_DEPTH = 2


def closest_pair_dc(points_a, points_b):
    """
    Encontra o par mais próximo entre points_a e points_b via Dividir e Conquistar.

    Junta os dois grupos, ordena por x e por y e aplica _rec recursivamente.
    O array y-sorted é propagado para cada sub-problema, eliminando o custo de
    re-ordenar a strip a cada nível.

    Retorna dict com:
        pair        – tupla (p1, p2) com os pontos mais próximos
        distance    – distância euclidiana entre eles
        comparisons – número total de comparações de distância realizadas
        time_ms     – tempo de execução em milissegundos
        steps       – lista de passos para animação da recursão
    """
    if not points_a or not points_b:
        raise ValueError("Ambas as listas devem conter ao menos um ponto.")

    all_points = points_a + points_b
    if len(all_points) < 2:
        raise ValueError("São necessários ao menos 2 pontos no total.")

    pts_x = sorted(all_points, key=lambda p: p["x"])
    pts_y = sorted(all_points, key=lambda p: p["y"])

    comparisons = 0
    steps = []

    def _rec(sub_x, sub_y, depth=0):
        nonlocal comparisons
        n = len(sub_x)

        if n <= 3:
            pair, dist, cnt = _brute_force_small(sub_x)
            comparisons += cnt
            return pair, dist

        mid = n // 2
        line_x = sub_x[mid]["x"]

        left_x  = sub_x[:mid]
        right_x = sub_x[mid:]
        # Divide y-sorted array by x-coordinate, preserving y order for both halves.
        left_y  = [p for p in sub_y if p["x"] <  line_x]
        right_y = [p for p in sub_y if p["x"] >= line_x]

        record = depth <= _ANIM_MAX_DEPTH
        divide_idx = None
        if record:
            divide_idx = len(steps)
            steps.append({
                "action": "divide", "line_L": line_x,
                "delta": None, "strip_points": [], "best_pair": None,
            })

        pair_l, dist_l = _rec(left_x,  left_y,  depth + 1)
        pair_r, dist_r = _rec(right_x, right_y, depth + 1)

        if dist_l <= dist_r:
            best_pair, delta = pair_l, dist_l
        else:
            best_pair, delta = pair_r, dist_r

        # sub_y already sorted by y — no strip.sort() needed.
        strip = [p for p in sub_y if abs(p["x"] - line_x) < delta]

        if record:
            steps[divide_idx]["delta"] = delta
            steps.append({
                "action": "strip", "line_L": line_x, "delta": delta,
                "strip_points": strip[:], "best_pair": best_pair,
            })

        for i in range(len(strip)):
            j = i + 1
            while j < len(strip) and (strip[j]["y"] - strip[i]["y"]) < delta:
                dist = euclidean_distance(strip[i], strip[j])
                comparisons += 1
                if dist < delta:
                    delta = dist
                    best_pair = (strip[i], strip[j])
                j += 1
                if j - i > 7:
                    break

        return best_pair, delta

    start = time.perf_counter()
    best_pair, best_dist = _rec(pts_x, pts_y)
    elapsed_ms = (time.perf_counter() - start) * 1000

    steps.append({
        "action": "result", "line_L": None, "delta": best_dist,
        "strip_points": [], "best_pair": best_pair,
    })

    return {
        "pair": best_pair,
        "distance": best_dist,
        "comparisons": comparisons,
        "time_ms": elapsed_ms,
        "steps": steps,
    }


def _brute_force_small(pts):
    """Base case: força bruta para n ≤ 3. Retorna (pair, distance, comparison_count)."""
    best_pair = None
    best_dist = math.inf
    count = 0
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            d = euclidean_distance(pts[i], pts[j])
            count += 1
            if d < best_dist:
                best_dist = d
                best_pair = (pts[i], pts[j])
    return best_pair, best_dist, count
