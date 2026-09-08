from pathlib import Path
import pandas as pd
from gap_engine import compute_gap

BASE_DIR = Path(__file__).resolve().parent
supply = pd.read_parquet(BASE_DIR / "supply_index.parquet")

# D здесь иллюстративный (синтетический) — реального спроса нет
demo_demand = pd.DataFrame([
    {"direction": "Общий менеджмент, принятие решений", "campus": "Москва", "year_start": 2024.0, "D": 1600},
    {"direction": "Право", "campus": "Москва", "year_start": 2024.0, "D": 90},
    {"direction": "Анализ данных(Data Science) и аналитика", "campus": "Москва", "year_start": 2024.0, "D": 220},
    {"direction": "Психология", "campus": "Москва", "year_start": 2024.0, "D": 60},
])

result = compute_gap(supply, demo_demand)
print("=== Демонстрация расчёта G(d,r,t) (D — иллюстративные данные) ===")
print(result[["direction", "campus", "S", "D", "G", "status"]].to_string(index=False))
