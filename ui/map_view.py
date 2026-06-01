"""
Visualização do mapa GPS e gráfico de comparação de performance com matplotlib.
"""

import os
import pathlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.animation import PillowWriter


_FIG_BG          = "#1a1a2e"   # fundo da figura
_PLOT_BG         = "#0d1117"   # fundo da área de plotagem
_GRID_COLOR      = "white"
_CAR_COLOR       = "#4FC3F7"
_PASSENGER_COLOR = "#EF5350"
_HIGHLIGHT_COLOR = "#FFD700"
_LINE_COLOR      = "#00E676"
_STRIP_COLOR     = "#FFD700"
_DIVIDE_COLOR    = "#ffffff"
_LEFT_COLOR      = "#81D4FA"   # pontos à esquerda da divisão
_RIGHT_COLOR     = "#FF8C42"   # pontos à direita da divisão
_MUTED_COLOR     = "#555577"   # pontos fora do foco
_LEGEND_DARK     = {"facecolor": "#1a1a2e", "edgecolor": "#444466", "labelcolor": "white"}
_LEGEND_RIGHT    = "upper right"

_ASSETS_DIR = pathlib.Path(__file__).parent.parent / "assets"
_ASSETS_DIR.mkdir(exist_ok=True)


def _asset(filename):
    return str(_ASSETS_DIR / filename)


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

    _draw_points(ax, cars, passengers)

    # Sobreposições de passo de animação
    if step is not None:
        action = step.get("action")
        line_l = step.get("line_L")
        delta  = step.get("delta")

        if action == "divide" and line_l is not None:
            ax.axvline(x=line_l, color=_DIVIDE_COLOR, linestyle="--", linewidth=1.2,
                       alpha=0.7, zorder=2, label="Divisao L")

        elif action == "strip" and line_l is not None and delta is not None:
            ax.axvline(x=line_l, color=_DIVIDE_COLOR, linestyle="--", linewidth=1.0,
                       alpha=0.5, zorder=2)
            ax.add_patch(mpatches.Rectangle(
                (line_l - delta, 0), width=2 * delta, height=1000,
                facecolor=_STRIP_COLOR, alpha=0.15, zorder=1, label=f"Faixa delta={delta:.1f}",
            ))

    if result is not None:
        _draw_result(ax, result, result["distance"])

    ax.set_xlim(0, 1000)
    ax.set_ylim(0, 1000)
    ax.set_title("GPS Inteligente — Par de Pontos Mais Proximos  O(n log n)",
                 color="white", fontsize=14, pad=15)
    ax.legend(**_LEGEND_DARK, fontsize=10, loc=_LEGEND_RIGHT)

    fig.tight_layout()
    fig.savefig(_asset("output_map.png"), dpi=150, facecolor=_FIG_BG)
    plt.show()
    plt.close(fig)


def draw_comparison(results):
    """
    Plota o gráfico de comparação de performance entre D&C e Força Bruta.

    Parâmetro:
        results – lista de dicts {"n": int, "time_brute": float, "time_dc": float}
    """
    if not results:
        raise ValueError("A lista de resultados esta vazia.")

    ns          = [r["n"] for r in results]
    times_brute = [r["time_brute"] for r in results]
    times_dc    = [r["time_dc"]    for r in results]

    fig, ax = _make_dark_axes(figsize=(10, 6))

    ax.plot(ns, times_dc,    color=_CAR_COLOR,       linewidth=2, marker="o",
            markersize=5, label="D&C — O(n log n)")
    ax.plot(ns, times_brute, color=_PASSENGER_COLOR, linewidth=2, marker="s",
            markersize=5, label="Forca Bruta — O(n²)")

    _annotate_endpoint(ax, ns[-1], times_dc[-1],    f"{times_dc[-1]:.2f} ms",    _CAR_COLOR)
    _annotate_endpoint(ax, ns[-1], times_brute[-1], f"{times_brute[-1]:.2f} ms", _PASSENGER_COLOR)

    ax.set_xlabel("Numero de pontos (n)", color="white", fontsize=11)
    ax.set_ylabel("Tempo (ms)",           color="white", fontsize=11)
    ax.set_title("Comparacao de Performance: O(n²) vs O(n log n)",
                 color="white", fontsize=14, pad=15)
    ax.legend(**_LEGEND_DARK, fontsize=10, loc="upper left")

    fig.tight_layout()
    fig.savefig(_asset("output_comparison.png"), dpi=150, facecolor=_FIG_BG)
    plt.show()
    plt.close(fig)


def animate_step_by_step(cars, passengers, steps, result):
    """
    Animação interativa passo a passo do algoritmo Dividir e Conquistar.

    Usa loop manual com plt.pause() para exibir cada frame ao vivo e
    PillowWriter.grab_frame() para salvar o GIF na mesma passagem,
    evitando renderizar cada frame duas vezes.
    """
    all_points   = cars + passengers
    total_frames = 1 + len(steps)

    plt.ion()
    fig, ax = _make_dark_axes(figsize=(10, 10))
    fig.tight_layout()
    plt.show(block=False)

    gif_path = _asset("output_animation.gif")
    writer = PillowWriter(fps=1 / 3)

    saved_divide = False
    saved_strip  = False

    with writer.saving(fig, gif_path, dpi=100):
        for frame_idx in range(total_frames):
            _render_frame(ax, frame_idx, steps, all_points, result, total_frames)
            fig.canvas.draw()
            fig.canvas.flush_events()
            writer.grab_frame(facecolor=_FIG_BG)

            # Auto-salva o primeiro frame de cada tipo para o README
            if frame_idx > 0:
                action = steps[frame_idx - 1].get("action")
                if action == "divide" and not saved_divide:
                    fig.savefig(_asset("divide_step.png"), dpi=150, facecolor=_FIG_BG)
                    saved_divide = True
                elif action == "strip" and not saved_strip:
                    fig.savefig(_asset("strip_step.png"), dpi=150, facecolor=_FIG_BG)
                    saved_strip = True

            plt.pause(3.0)

    plt.ioff()
    plt.close(fig)
    print(f"  GIF salvo em: {gif_path}")



# ---------------------------------------------------------------------------
# Helpers privados
# ---------------------------------------------------------------------------

def _reset_ax(ax):
    """Limpa o eixo e reaplica o estilo escuro padrão."""
    ax.cla()
    ax.set_facecolor(_PLOT_BG)
    ax.grid(True, color=_GRID_COLOR, linewidth=0.5, linestyle="-", alpha=0.15)
    ax.tick_params(colors="white")
    for spine in ax.spines.values():
        spine.set_edgecolor("#333355")
    ax.set_xlim(0, 1000)
    ax.set_ylim(0, 1000)


def _draw_points(ax, cars, passengers):
    """Plota carros e passageiros no eixo."""
    if cars:
        ax.scatter(
            [p["x"] for p in cars],
            [p["y"] for p in cars],
            c=_CAR_COLOR, marker="^", s=120, edgecolors="white",
            linewidths=0.5, label="Carros", zorder=3,
        )
    if passengers:
        ax.scatter(
            [p["x"] for p in passengers],
            [p["y"] for p in passengers],
            c=_PASSENGER_COLOR, marker="o", s=120, edgecolors="white",
            linewidths=0.5, label="Passageiros", zorder=3,
        )


def _apply_step(ax, step, result):
    """Aplica a sobreposição visual correspondente ao action do step."""
    action = step.get("action")
    line_l = step.get("line_L")
    delta  = step.get("delta")

    if action == "divide" and line_l is not None:
        ax.axvline(x=line_l, color=_DIVIDE_COLOR, linestyle="--",
                   linewidth=1.4, alpha=0.8, zorder=2, label="Divisao L")
        ax.set_title(f"Dividindo em x={line_l:.0f}", color="white", fontsize=14, pad=15)

    elif action == "strip" and line_l is not None and delta is not None:
        ax.axvline(x=line_l, color=_DIVIDE_COLOR, linestyle="--",
                   linewidth=1.0, alpha=0.5, zorder=2)
        ax.add_patch(mpatches.Rectangle(
            (line_l - delta, 0), width=2 * delta, height=1000,
            facecolor=_STRIP_COLOR, alpha=0.15, zorder=1, label=f"Faixa delta={delta:.1f}",
        ))
        ax.set_title(f"Checando faixa 2delta = {2 * delta:.1f}", color="white", fontsize=14, pad=15)

    elif action == "result":
        _draw_result(ax, result, delta)


def _draw_result(ax, result, delta):
    """Destaca o par final com estrela amarela, linha tracejada verde e label de distância."""
    p1, p2 = result["pair"]
    dist   = result["distance"]

    ax.scatter([p1["x"], p2["x"]], [p1["y"], p2["y"]],
               c=_HIGHLIGHT_COLOR, marker="*", s=400, zorder=5, label="Par mais proximo",
               edgecolors="white", linewidths=0.5)
    ax.plot([p1["x"], p2["x"]], [p1["y"], p2["y"]],
            color=_LINE_COLOR, linewidth=2, linestyle="--", zorder=4)
    ax.text(
        (p1["x"] + p2["x"]) / 2, (p1["y"] + p2["y"]) / 2,
        f"  dist = {dist:.2f}",
        color=_LINE_COLOR, fontsize=11, va="bottom",
        bbox={"facecolor": "white", "edgecolor": _LINE_COLOR, "alpha": 0.9, "boxstyle": "round,pad=0.3"},
    )
    title_delta = delta if delta is not None else dist
    ax.set_title(f"Par mais proximo encontrado!  dist = {title_delta:.2f}",
                 color=_HIGHLIGHT_COLOR, fontsize=14, pad=15)


def _render_frame(ax, frame_idx, steps, all_points, result, total_frames):
    """Desenha um frame completo — usado tanto no loop ao vivo quanto no GIF."""
    _reset_ax(ax)
    if frame_idx == 0:
        _draw_points_from_list(ax, all_points)
        ax.set_title("Todos os pontos — iniciando busca...",
                     color="white", fontsize=14, pad=15)
    else:
        step = steps[frame_idx - 1]
        last_strip = None
        if step["action"] == "result":
            last_strip = next(
                (s for s in reversed(steps[:frame_idx - 1]) if s["action"] == "strip"),
                None,
            )
        _draw_step_frame(ax, step, all_points, result, last_strip)

    counter = "Inicio" if frame_idx == 0 else f"Passo {frame_idx} de {total_frames - 1}"
    ax.text(0.98, 0.02, counter, transform=ax.transAxes,
            ha="right", va="bottom", color="white", fontsize=9,
            bbox={"facecolor": "#1a1a2e", "edgecolor": "none", "alpha": 0.75})
    ax.legend(**_LEGEND_DARK, fontsize=10, loc=_LEGEND_RIGHT)


def _draw_points_from_list(ax, all_points):
    """Plota todos os pontos de uma lista mista usando cor e marcador por type."""
    cars       = [p for p in all_points if p["type"] == "car"]
    passengers = [p for p in all_points if p["type"] == "passenger"]
    _draw_points(ax, cars, passengers)


def _draw_step_frame(ax, step, all_points, result, last_strip=None):
    """Despacha para o helper correto conforme o action do step."""
    action = step.get("action")
    if action == "divide":
        _draw_frame_divide(ax, step, all_points)
    elif action == "strip":
        _draw_frame_strip(ax, step, all_points)
    elif action == "result":
        _draw_frame_result(ax, step, all_points, result, last_strip)


def _draw_frame_divide(ax, step, all_points):
    """Frame de divisão: pontos coloridos por lado, linha L tracejada."""
    line_l = step["line_L"]
    left  = [p for p in all_points if p["x"] <  line_l]
    right = [p for p in all_points if p["x"] >= line_l]

    if left:
        ax.scatter([p["x"] for p in left], [p["y"] for p in left],
                   c=_LEFT_COLOR, marker="o", s=90, edgecolors="white",
                   linewidths=0.4, label="Esquerda", zorder=3)
    if right:
        ax.scatter([p["x"] for p in right], [p["y"] for p in right],
                   c=_RIGHT_COLOR, marker="o", s=90, edgecolors="white",
                   linewidths=0.4, label="Direita", zorder=3)

    ax.axvline(x=line_l, color=_DIVIDE_COLOR, linestyle="--", linewidth=1.5,
               alpha=0.9, zorder=4, label="Linha L")

    delta = step.get("delta")
    delta_str = f"{delta:.1f}" if delta is not None else "---"
    ax.set_title(f"Dividindo: L = {line_l:.0f}  |  delta atual = {delta_str}",
                 color="white", fontsize=14, pad=15)


def _draw_frame_strip(ax, step, all_points):
    """Frame de faixa: pontos na faixa destacados, retângulo amarelo sombreado."""
    line_l = step["line_L"]
    delta  = step["delta"]
    strip_xy = {(p["x"], p["y"]) for p in step.get("strip_points", [])}

    in_strip  = [p for p in all_points if (p["x"], p["y"]) in strip_xy]
    out_strip = [p for p in all_points if (p["x"], p["y"]) not in strip_xy]

    if out_strip:
        ax.scatter([p["x"] for p in out_strip], [p["y"] for p in out_strip],
                   c=_MUTED_COLOR, marker="o", s=60, edgecolors="white",
                   linewidths=0.3, alpha=0.4, zorder=3)
    if in_strip:
        ax.scatter([p["x"] for p in in_strip], [p["y"] for p in in_strip],
                   c=_HIGHLIGHT_COLOR, marker="o", s=130, edgecolors="white",
                   linewidths=0.5, label="Na faixa", zorder=4)

    ax.axvline(x=line_l, color=_DIVIDE_COLOR, linestyle="--", linewidth=1.0,
               alpha=0.6, zorder=2)
    ax.add_patch(mpatches.Rectangle(
        (line_l - delta, 0), width=2 * delta, height=1000,
        facecolor=_STRIP_COLOR, alpha=0.2, zorder=1,
    ))
    ax.set_title(
        f"Checando faixa 2delta = {2 * delta:.1f} — {len(in_strip)} pontos",
        color="white", fontsize=14, pad=15,
    )


def _draw_frame_result(ax, step, all_points, result, last_strip=None):
    """Frame final: linha L + faixa do último strip, par destacado com estrela e caixa."""
    p1, p2 = result["pair"]
    dist   = step.get("delta") or result["distance"]

    ax.scatter([p["x"] for p in all_points], [p["y"] for p in all_points],
               c=_MUTED_COLOR, marker="o", s=60, edgecolors="white",
               linewidths=0.3, alpha=0.35, zorder=3)

    if last_strip is not None:
        line_l = last_strip["line_L"]
        delta  = last_strip["delta"]
        ax.axvline(x=line_l, color=_DIVIDE_COLOR, linestyle="--",
                   linewidth=1.0, alpha=0.5, zorder=2)
        ax.add_patch(mpatches.Rectangle(
            (line_l - delta, 0), width=2 * delta, height=1000,
            facecolor=_STRIP_COLOR, alpha=0.15, zorder=1,
        ))

    ax.scatter([p1["x"], p2["x"]], [p1["y"], p2["y"]],
               c=_HIGHLIGHT_COLOR, marker="*", s=400, edgecolors="white",
               linewidths=0.5, label="Par mais proximo", zorder=5)
    ax.plot([p1["x"], p2["x"]], [p1["y"], p2["y"]],
            color=_LINE_COLOR, linewidth=2, linestyle="--", zorder=4)
    ax.text(
        (p1["x"] + p2["x"]) / 2, (p1["y"] + p2["y"]) / 2,
        f"Par encontrado! dist = {dist:.2f}",
        color=_LINE_COLOR, fontsize=11, va="bottom",
        bbox={"facecolor": "white", "edgecolor": _LINE_COLOR,
              "alpha": 0.9, "boxstyle": "round,pad=0.3"},
    )
    ax.set_title("Par mais proximo encontrado!", color=_HIGHLIGHT_COLOR, fontsize=14, pad=15)


def _make_dark_axes(figsize):
    """Cria figura e eixo com tema escuro padronizado."""
    fig, ax = plt.subplots(figsize=figsize, facecolor=_FIG_BG)
    ax.set_facecolor(_PLOT_BG)
    ax.grid(True, color=_GRID_COLOR, linewidth=0.5, linestyle="-", alpha=0.15)
    ax.tick_params(colors="white")
    for spine in ax.spines.values():
        spine.set_edgecolor("#333355")
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
