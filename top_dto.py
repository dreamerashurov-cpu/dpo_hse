from pathlib import Path
import pandas as pd
import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["font.family"] = "DejaVu Sans"

from dashboard import top_directions, build_top_directions_png

BASE_DIR = Path(__file__).resolve().parent
programs = pd.read_parquet(BASE_DIR / "programs.parquet")
top5 = top_directions(programs, n=5)
print(top5.to_string(index=False))

build_top_directions_png(top5, str(BASE_DIR / "top_directions.png"))
print("Сохранено в top_directions.png")
