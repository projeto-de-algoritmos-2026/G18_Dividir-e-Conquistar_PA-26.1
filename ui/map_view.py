"""
Visualização do mapa GPS e gráfico de comparação de performance com matplotlib.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


_BG_COLOR = "#1a1a2e"
_GRID_COLOR = "#2a2a4e"
_CAR_COLOR = "#4fc3f7"
_PASSENGER_COLOR = "#ef5350"
_HIGHLIGHT_COLOR = "#ffd600"
_LINE_COLOR = "#69f0ae"
_STRIP_COLOR = "#ffd600"
_DIVIDE_COLOR = "#ffffff"


def draw_map(cars, passengers, result=None, step=None):
    """
    Renderiza o mapa GPS com carros, passageiros e resultado do algoritmo.

    Parâmetros:
        cars       – lista de dicts com campos x, y, name, type
        passengers – lista de dicts com campos x, y, name, type
        result     – dict retornado por closest_pair_dc ou brute_force_closest
        step       – dict de um passo de animação (keys: action, line_L, delta, ...)
    """
    fig, ax = _make_dark_axes(figsize=(10, 10))

    # Pontos base
    if cars:
        ax.scatter(
            [p["x"] for p in cars],
            [p["y"] for p in cars],
            c=_CAR_COLOR, marker="^", s=100, label="Carros", zorder=3,
        )

    if passengers:
        ax.scatter(
            [p["x"] for p in passengers],
            [p["y"] for p in passengers],
            c=_PASSENGER_COLOR, marker="o", s=100, label="Passageiros", zorder=3,
        )

    # Sobreposições de passo de animação
    if step is not None:
        action = step.get("action")
        line_l = step.get("line_L")
        delta = step.get("delta")

        if action == "divide" and line_l is not None:
            ax.axvline(x=line_l, color=_DIVIDE_COLOR, linestyle="--", linewidth=1.2,
                       alpha=0.7, zorder=2, label="Divisão L")

        elif action == "strip" and line_l is not None and delta is not None:
            ax.axvline(x=line_l, color=_DIVIDE_COLOR, linestyle="--", linewidth=1.0,
                       alpha=0.5, zorder=2)
            strip_rect = mpatches.Rectangle(
                (line_l - delta, 0), width=2 * delta, height=1000,
                facecolor=_STRIP_COLOR, alpha=0.15, zorder=1, label=f"Faixa δ={delta:.1f}",
            )
            ax.add_patch(strip_rect)

    # Destaque do par mais próximo
    if result is not None:
        p1, p2 = result["pair"]
        dist = result["distance"]

        ax.scatter([p1["x"], p2["x"]], [p1["y"], p2["y"]],
                   c=_HIGHLIGHT_COLOR, marker="*", s=300, zorder=5, label="Par mais próximo")

        ax.plot([p1["x"], p2["x"]], [p1["y"], p2["y"]],
                color=_LINE_COLOR, linewidth=1.8, zorder=4)

        mid_x = (p1["x"] + p2["x"]) / 2
        mid_y = (p1["y"] + p2["y"]) / 2
        ax.text(mid_x, mid_y, f"  dist = {dist:.1f}",
                color=_LINE_COLOR, fontsize=9, va="bottom",
                bbox={"facecolor": _BG_COLOR, "edgecolor": "none", "alpha": 0.7})

    ax.set_xlim(0, 1000)
    ax.set_ylim(0, 1000)
    ax.set_title("GPS Inteligente — Par de Pontos O(n log n)",
                 color="white", fontsize=13, pad=12)
    ax.legend(facecolor="#2a2a4e", edgecolor="none", labelcolor="white",
              fontsize=9, loc="upper right")

    fig.tight_layout()
    fig.savefig("output_map.png", dpi=150, facecolor=_BG_COLOR)
    plt.show()
    plt.close(fig)


def draw_comparison(results):
    """
    Plota o gráfico de comparação de performance entre D&C e Força Bruta.

    Parâmetro:
        results – lista de dicts {"n": int, "time_brute": float, "time_dc": float}
    """
    if not results:
        raise ValueError("A lista de resultados está vazia.")

    ns = [r["n"] for r in results]
    times_brute = [r["time_brute"] for r in results]
    times_dc = [r["time_dc"] for r in results]

    fig, ax = _make_dark_axes(figsize=(10, 6))

    ax.plot(ns, times_dc, color=_CAR_COLOR, linewidth=2, marker="o",
            markersize=5, label="D&C — O(n log n)")
    ax.plot(ns, times_brute, color=_PASSENGER_COLOR, linewidth=2, marker="s",
            markersize=5, label="Força Bruta — O(n²)")

    # Anotação no último ponto de cada série
    _annotate_endpoint(ax, ns[-1], times_dc[-1], f"{times_dc[-1]:.2f} ms", _CAR_COLOR)
    _annotate_endpoint(ax, ns[-1], times_brute[-1], f"{times_brute[-1]:.2f} ms", _PASSENGER_COLOR)

    ax.set_xlabel("Número de pontos (n)", color="white", fontsize=11)
    ax.set_ylabel("Tempo (ms)", color="white", fontsize=11)
    ax.set_title("Comparação de Performance: O(n²) vs O(n log n)",
                 color="white", fontsize=13, pad=12)
    ax.legend(facecolor="#2a2a4e", edgecolor="none", labelcolor="white",
              fontsize=10, loc="upper left")

    fig.tight_layout()
    fig.savefig("output_comparison.png", dpi=150, facecolor=_BG_COLOR)
    plt.show()
    plt.close(fig)


# ---------------------------------------------------------------------------
# Helpers privados
# ---------------------------------------------------------------------------

def _make_dark_axes(figsize):
    """Cria figura e eixo com tema escuro padronizado."""
    fig, ax = plt.subplots(figsize=figsize, facecolor=_BG_COLOR)
    ax.set_facecolor(_BG_COLOR)
    ax.grid(True, color=_GRID_COLOR, linewidth=0.6, linestyle="-")
    ax.tick_params(colors="white")
    for spine in ax.spines.values():
        spine.set_edgecolor(_GRID_COLOR)
    return fig, ax


def _annotate_endpoint(ax, x, y, label, color):
    """Anota o valor no final de uma linha do gráfico de comparação."""
    ax.annotate(
        label,
        xy=(x, y),
        xytext=(8, 0),
        textcoords="offset points",
        color=color,
        fontsize=9,
        va="center",
    )
