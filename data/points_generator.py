"""
Geração de conjuntos de pontos simulando coordenadas GPS de carros e passageiros.
"""

import random


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


def generate_city_scenario(n_cars=20, n_passengers=20):
    """
    Gera um cenário urbano com carros e passageiros sem sobreposição.

    Usa seeds distintas para carros e passageiros garantindo que os dois grupos
    não compartilhem posições idênticas mesmo quando n_cars == n_passengers.

    Retorna:
        (cars, passengers): tupla com as duas listas de dicts.
    """
    MIN_DISTANCE = 1.0

    def _generate_points(n, label, point_type, seed, existing):
        rng = random.Random(seed)
        points = []
        attempts = 0
        max_attempts = n * 1000

        while len(points) < n and attempts < max_attempts:
            attempts += 1
            candidate = {"name": f"{label}_{len(points) + 1}",
                         "x": round(rng.uniform(0, 1000), 4),
                         "y": round(rng.uniform(0, 1000), 4),
                         "type": point_type}

            all_points = existing + points
            if all(_euclidean(candidate, p) >= MIN_DISTANCE for p in all_points):
                points.append(candidate)

        if len(points) < n:
            raise RuntimeError(
                f"Não foi possível posicionar {n} pontos sem sobreposição "
                f"após {max_attempts} tentativas."
            )
        return points

    cars = _generate_points(n_cars, "Carro", "car", seed=42, existing=[])
    passengers = _generate_points(n_passengers, "Passageiro", "passenger", seed=99, existing=cars)
    return cars, passengers


def _euclidean(a, b):
    return ((a["x"] - b["x"]) ** 2 + (a["y"] - b["y"]) ** 2) ** 0.5
