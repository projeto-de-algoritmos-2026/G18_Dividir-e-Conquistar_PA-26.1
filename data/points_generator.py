"""
Geração de conjuntos de pontos simulando coordenadas GPS de carros e passageiros.
"""

import random

from algorithms.utils import euclidean_distance


def generate_cars(n, seed=None):
    """Gera n carros com posições aleatórias no plano 1000x1000."""
    rng = random.Random(seed)
    return [
        {"name": f"Carro_{i + 1}", "x": rng.uniform(0, 1000), "y": rng.uniform(0, 1000), "type": "car"}
        for i in range(n)
    ]


def generate_passengers(n, seed=None):
    """Gera n passageiros com posições aleatórias no plano 1000x1000."""
    rng = random.Random(seed)
    return [
        {"name": f"Passageiro_{i + 1}", "x": rng.uniform(0, 1000), "y": rng.uniform(0, 1000), "type": "passenger"}
        for i in range(n)
    ]


def generate_city_scenario(n_cars=20, n_passengers=20, seed=None):
    """
    Gera um cenário urbano com carros e passageiros sem sobreposição.

    Parâmetros:
        n_cars, n_passengers – quantidade de pontos em cada grupo.
        seed – semente para reprodutibilidade; None mantém seeds padrão (42 / 99).

    Retorna:
        (cars, passengers): tupla com as duas listas de dicts.
    """
    MIN_DISTANCE = 1.0
    seed_cars = 42 if seed is None else seed
    seed_pass = 99 if seed is None else seed * 7 + 1

    def _generate_points(n, label, point_type, rng_seed, existing):
        rng = random.Random(rng_seed)
        points = []
        attempts = 0
        max_attempts = n * 1000

        while len(points) < n and attempts < max_attempts:
            attempts += 1
            candidate = {
                "name": f"{label}_{len(points) + 1}",
                "x": round(rng.uniform(0, 1000), 4),
                "y": round(rng.uniform(0, 1000), 4),
                "type": point_type,
            }
            if all(euclidean_distance(candidate, p) >= MIN_DISTANCE for p in existing + points):
                points.append(candidate)

        if len(points) < n:
            raise RuntimeError(
                f"Não foi possível posicionar {n} pontos sem sobreposição "
                f"após {max_attempts} tentativas."
            )
        return points

    cars       = _generate_points(n_cars,       "Carro",      "car",       seed_cars, existing=[])
    passengers = _generate_points(n_passengers, "Passageiro", "passenger", seed_pass, existing=cars)
    return cars, passengers
