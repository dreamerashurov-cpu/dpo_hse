from pathlib import Path
import pandas as pd
import plotly.express as px
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

matplotlib.rcParams["font.family"] = "DejaVu Sans"


def summary_stats(programs: pd.DataFrame) -> dict:
    return {
        "total_programs": len(programs),
        "total_hours": programs["hours"].sum(),
        "total_listeners": programs["listeners_actual"].sum(),
        "n_directions": programs["direction"].nunique(),
        "n_campuses": programs["campus"].nunique(),
    }


def top_directions(programs: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    return (
        programs.groupby("direction")
        .size()
        .sort_values(ascending=False)
        .head(n)
        .reset_index(name="n_programs")
    )


def build_heatmap(programs: pd.DataFrame, top_n_directions: int = 15):
    top_dirs = programs["direction"].value_counts().head(top_n_directions).index
    subset = programs[programs["direction"].isin(top_dirs)]

    pivot = (
        subset.groupby(["direction", "campus"])
        .size()
        .reset_index(name="n_programs")
        .pivot(index="direction", columns="campus", values="n_programs")
        .fillna(0)
    )

    fig = px.imshow(
        pivot,
        labels=dict(x="Кампус", y="Направление подготовки", color="Число программ"),
        color_continuous_scale="Blues",
        aspect="auto",
        title="Тепловая карта предложения программ ДПО НИУ ВШЭ (топ-15 направлений)",
    )
    fig.update_layout(width=900, height=700, margin=dict(l=250))
    return fig


def build_top_directions_png(top5: pd.DataFrame, path: str) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    colors = ["#c0392b" if d == "Не указано" else "#2e6da4" for d in top5["direction"]]
    bars = ax.barh(top5["direction"][::-1], top5["n_programs"][::-1], color=colors[::-1])
    ax.set_xlabel("Число программ")
    ax.set_title("Топ-5 направлений подготовки по числу программ ДПО\n(НИУ ВШЭ, 2024–2026)")
    for bar, value in zip(bars, top5["n_programs"][::-1]):
        ax.text(value + 15, bar.get_y() + bar.get_height() / 2, str(int(value)),
                va="center", fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def build_heatmap_static_png(programs: pd.DataFrame, path: str, top_n_directions: int = 15):
    # matplotlib вместо plotly — Kaleido/Chrome тут недоступны
    top_dirs = programs["direction"].value_counts().head(top_n_directions).index
    subset = programs[programs["direction"].isin(top_dirs)]
    pivot = (
        subset.groupby(["direction", "campus"])
        .size()
        .reset_index(name="n_programs")
        .pivot(index="direction", columns="campus", values="n_programs")
        .fillna(0)
    )
    pivot = pivot.loc[top_dirs]  # сохраняем порядок по убыванию частоты

    fig, ax = plt.subplots(figsize=(8, 8))
    im = ax.imshow(pivot.values, cmap="Blues", aspect="auto")
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, rotation=30, ha="right")
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            v = int(pivot.values[i, j])
            if v > 0:
                ax.text(j, i, str(v), ha="center", va="center",
                        color="white" if v > pivot.values.max() / 2 else "black", fontsize=8)
    ax.set_title("Тепловая карта предложения программ ДПО НИУ ВШЭ\n(топ-15 направлений по кампусам)")
    fig.colorbar(im, ax=ax, label="Число программ")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent
    programs = pd.read_parquet(BASE_DIR / "programs.parquet")

    stats = summary_stats(programs)
    print("=== FR-1.1 Сводная панель ===")
    for k, v in stats.items():
        print(f"{k}: {v}")

    print("\n=== FR-1.3 Топ-5 направлений ===")
    print(top_directions(programs).to_string(index=False))

    print("\n=== FR-2 Построение тепловой карты ===")
    build_heatmap_static_png(programs, str(BASE_DIR / "heatmap.png"))
    print("Сохранено в heatmap.png")
