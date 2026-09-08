from pathlib import Path
import pandas as pd


def compute_supply_index(programs: pd.DataFrame) -> pd.DataFrame:
    df = programs.copy()
    df["listeners_actual"] = df["listeners_actual"].fillna(0)

    supply = (
        df.groupby(["direction", "campus", "year_start"], dropna=False)
        .agg(
            n_programs=("program_id", "count"),
            total_hours=("hours", "sum"),
            total_listeners=("listeners_actual", "sum"),
        )
        .reset_index()
    )
    # S — объём программ, взвешенный по числу слушателей
    supply["S"] = supply["n_programs"] * (1 + supply["total_listeners"] / 100)
    return supply


def compute_gap(supply: pd.DataFrame, demand: pd.DataFrame) -> pd.DataFrame:
    merged = supply.merge(demand, on=["direction", "campus", "year_start"], how="inner")
    # G > 0 — дефицит (спрос выше предложения), G <= 0 — профицит
    merged["G"] = (merged["D"] - merged["S"]) / merged["D"]

    def classify(g):
        if g > 0.3:
            return "критический дефицит"
        elif g > 0:
            return "умеренный дефицит"
        else:
            return "профицит"

    merged["status"] = merged["G"].apply(classify)
    return merged


if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent
    programs = pd.read_parquet(BASE_DIR / "programs.parquet")
    supply = compute_supply_index(programs)
    print(f"Строк в индексе предложения S(d,r,t): {len(supply)}")
    print(supply.sort_values("S", ascending=False).head(5).to_string(index=False))
    supply.to_parquet(BASE_DIR / "supply_index.parquet", index=False)
