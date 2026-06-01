"""
Ponto de entrada da aplicação GPS Inteligente — Dividir e Conquistar.
"""

from data.points_generator import generate_city_scenario, generate_cars, generate_passengers
from algorithms.brute_force import brute_force_closest
from algorithms.closest_pair import closest_pair_dc
from ui.map_view import draw_map, draw_comparison, animate_step_by_step

_SEP  = "=" * 52
_LINE = "-" * 52


def run_performance_test():
    """
    Mede e compara o tempo dos dois algoritmos para tamanhos crescentes de n.

    Retorna lista de dicts {"n", "time_brute", "time_dc"} pronta para draw_comparison.
    """
    sizes = [5, 10, 20, 50, 100, 200, 500]
    results = []

    print(f"\n{'TESTE DE PERFORMANCE':^52}")
    print(_SEP)
    print(f"  {'n':>5}  {'Bruta (ms)':>12}  {'D&C (ms)':>10}  {'Speedup':>9}")
    print(_LINE)

    for n in sizes:
        cars       = generate_cars(n, seed=n)
        passengers = generate_passengers(n, seed=n * 7)

        bf = brute_force_closest(cars, passengers)
        dc = closest_pair_dc(cars, passengers)

        speedup = bf["time_ms"] / dc["time_ms"] if dc["time_ms"] > 0 else float("inf")
        print(f"  {n:>5}  {bf['time_ms']:>12.4f}  {dc['time_ms']:>10.4f}  {speedup:>8.2f}x")

        results.append({"n": n, "time_brute": bf["time_ms"], "time_dc": dc["time_ms"]})

    print(_SEP)
    return results


def main():
    print(_SEP)
    print(f"{'GPS Inteligente - Dividir e Conquistar':^52}")
    print(_SEP)

    # 1. Gera cenário
    print(f"\n{'CENARIO':^52}")
    print(_LINE)
    cars, passengers = generate_city_scenario(n_cars=20, n_passengers=20)
    print(f"  {'Carros':<14}: {len(cars)}")
    print(f"  {'Passageiros':<14}: {len(passengers)}")

    # 2. Força bruta
    print(f"\n{'FORCA BRUTA  [O(n^2)]':^52}")
    print(_LINE)
    bf = brute_force_closest(cars, passengers)
    p1_bf, p2_bf = bf["pair"]
    print(f"  {'Par':<14}: {p1_bf['name']}  <->  {p2_bf['name']}")
    print(f"  {'Distancia':<14}: {bf['distance']:.4f}")
    print(f"  {'Comparacoes':<14}: {bf['comparisons']}")
    print(f"  {'Tempo':<14}: {bf['time_ms']:.4f} ms")

    # 3. Dividir e Conquistar
    print(f"\n{'DIVIDIR E CONQUISTAR  [O(n log n)]':^52}")
    print(_LINE)
    dc = closest_pair_dc(cars, passengers)
    p1_dc, p2_dc = dc["pair"]
    print(f"  {'Par':<14}: {p1_dc['name']}  <->  {p2_dc['name']}")
    print(f"  {'Distancia':<14}: {dc['distance']:.4f}")
    print(f"  {'Comparacoes':<14}: {dc['comparisons']}")
    print(f"  {'Tempo':<14}: {dc['time_ms']:.4f} ms")
    print(f"  {'Passos':<14}: {len(dc['steps'])}")

    # 4. Validação de corretude
    if abs(bf["distance"] - dc["distance"]) > 1e-9:
        raise ValueError(
            f"Distancias divergem: bruta={bf['distance']:.6f}  dc={dc['distance']:.6f}"
        )

    # 5. Resultado final + speedup
    print(f"\n{_SEP}")
    print(f"{'RESULTADO FINAL':^52}")
    print(_LINE)
    print(f"  Par mais proximo: {p1_dc['name']} <-> {p2_dc['name']} | distancia: {dc['distance']:.2f}")
    if dc["time_ms"] > 0:
        speedup = bf["time_ms"] / dc["time_ms"]
        print(f"  D&C foi {speedup:.1f}x mais rapido que a Forca Bruta!")
    else:
        print("  D&C foi mais rapido (tempo imensuravel em ms).")
    print(_SEP)

    # 6. Mapa estático com resultado destacado
    print("\nGerando mapa... (salvo em assets/output_map.png)")
    draw_map(cars, passengers, result=dc)

    # 7. Animação opcional
    resposta = input("\nVer animacao passo a passo? (s/n): ").strip().lower()
    if resposta == "s":
        print(f"Animando {len(dc['steps'])} passos...")
        animate_step_by_step(cars, passengers, dc["steps"], dc)

    # 8. Gráfico de comparação opcional
    resposta = input("\nVer comparacao de performance? (s/n): ").strip().lower()
    if resposta == "s":
        perf_results = run_performance_test()
        print("\nGerando grafico... (salvo em assets/output_comparison.png)")
        draw_comparison(perf_results)


if __name__ == "__main__":
    main()
