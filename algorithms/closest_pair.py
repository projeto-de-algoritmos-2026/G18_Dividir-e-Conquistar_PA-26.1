"""
Implementação do algoritmo Par de Pontos Mais Próximos via Dividir e Conquistar.

Complexidade: O(n log n), onde n = |points_a| + |points_b|.
A faixa central (strip) garante que no máximo 7 vizinhos precisam ser checados
por ponto, mantendo o passo de combinação em O(n).
"""

import math
import time


def euclidean_distance(p1, p2):
    """Distância euclidiana entre dois pontos com campos 'x' e 'y'."""
    return math.sqrt((p1["x"] - p2["x"]) ** 2 + (p1["y"] - p2["y"]) ** 2)


def closest_pair_dc(points_a, points_b):
    """
    Encontra o par mais próximo entre points_a e points_b via Dividir e Conquistar.

    Junta os dois grupos, ordena por x e aplica _closest_rec recursivamente.
    O contexto de cada ponto é preservado (campo 'type' indica car/passenger).

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

    pts_sorted_x = sorted(all_points, key=lambda p: p["x"])

    comparisons = [0]
    steps = []

    start = time.perf_counter()
    best_pair, best_dist = _closest_rec(pts_sorted_x, comparisons, steps, depth=0)
    elapsed_ms = (time.perf_counter() - start) * 1000

    steps.append({
        "action": "result",
        "line_L": None,
        "delta": best_dist,
        "strip_points": [],
        "best_pair": best_pair,
    })

    print(f"  [D&C] Passos gravados para animacao: {len(steps)}")

    return {
        "pair": best_pair,
        "distance": best_dist,
        "comparisons": comparisons[0],
        "time_ms": elapsed_ms,
        "steps": steps,
    }


def _brute_force_rec(pts, comparisons):
    """Força bruta usada na base da recursão (n ≤ 3)."""
    best_pair = None
    best_dist = math.inf

    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            dist = euclidean_distance(pts[i], pts[j])
            comparisons[0] += 1
            if dist < best_dist:
                best_dist = dist
                best_pair = (pts[i], pts[j])

    return best_pair, best_dist


_MAX_ANIM_DEPTH = 2  # grava steps apenas nos 3 níveis mais externos da recursão


def _closest_rec(pts_sorted_x, comparisons, steps, depth=0):
    """
    Recursão principal do Dividir e Conquistar.

    pts_sorted_x deve estar ordenado por x antes da chamada.
    comparisons é uma lista de um elemento usada como contador mutável.
    steps acumula os eventos dos primeiros _MAX_ANIM_DEPTH níveis para animação.
    """
    n = len(pts_sorted_x)

    if n <= 3:
        return _brute_force_rec(pts_sorted_x, comparisons)

    mid = n // 2
    line_x = pts_sorted_x[mid]["x"]
    left   = pts_sorted_x[:mid]
    right  = pts_sorted_x[mid:]

    record = depth <= _MAX_ANIM_DEPTH

    # Registra divide antes da recursão para preservar a ordem de animação.
    # delta é preenchido depois, quando a recursão retorna.
    divide_idx = None
    if record:
        divide_idx = len(steps)
        steps.append({
            "action": "divide",
            "line_L": line_x,
            "delta": None,
            "strip_points": [],
            "best_pair": None,
        })

    pair_left,  dist_left  = _closest_rec(left,  comparisons, steps, depth + 1)
    pair_right, dist_right = _closest_rec(right, comparisons, steps, depth + 1)

    if dist_left <= dist_right:
        best_pair, delta = pair_left, dist_left
    else:
        best_pair, delta = pair_right, dist_right

    strip = [p for p in pts_sorted_x if abs(p["x"] - line_x) < delta]
    strip.sort(key=lambda p: p["y"])

    if record:
        steps[divide_idx]["delta"] = delta
        steps.append({
            "action": "strip",
            "line_L": line_x,
            "delta": delta,
            "strip_points": strip[:],
            "best_pair": best_pair,
        })

    for i in range(len(strip)):
        j = i + 1
        while j < len(strip) and (strip[j]["y"] - strip[i]["y"]) < delta:
            dist = euclidean_distance(strip[i], strip[j])
            comparisons[0] += 1
            if dist < delta:
                delta = dist
                best_pair = (strip[i], strip[j])
            j += 1
            if j - i > 7:
                break

    return best_pair, delta
