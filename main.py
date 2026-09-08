"""Точка входа: данные ДПО НИУ ВШЭ -> дашборды + ИИ-прогноз."""
import argparse
import os
from pathlib import Path

import pandas as pd

import ai_forecast
import data_ingestion
import dashboard
from gap_engine import compute_supply_index

BASE_DIR = Path(__file__).resolve().parent


def load_dotenv() -> None:
    env_path = BASE_DIR / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--direction", default=None, help="Фокус ИИ-прогноза на направлении")
    parser.add_argument("--model", default=ai_forecast.DEFAULT_MODEL, help="Модель OpenAI")
    parser.add_argument("--output-dir", default="output", help="Папка для дашбордов и прогноза")
    parser.add_argument("--skip-ai", action="store_true", help="Не вызывать GPT API")
    return parser.parse_args()


def load_or_ingest_programs() -> pd.DataFrame:
    programs_path = BASE_DIR / "programs.parquet"
    if not programs_path.exists():
        print("programs.parquet не найден — запускаю ingestion из programs.xls...")
        programs = data_ingestion.load_programs()
        programs.to_parquet(programs_path, index=False)
    return pd.read_parquet(programs_path)


def main() -> None:
    load_dotenv()
    args = parse_args()
    output_dir = BASE_DIR / args.output_dir
    output_dir.mkdir(exist_ok=True)

    programs = load_or_ingest_programs()

    supply = compute_supply_index(programs)
    supply.to_parquet(BASE_DIR / "supply_index.parquet", index=False)

    stats = dashboard.summary_stats(programs)
    print("=== Сводная панель ===")
    for k, v in stats.items():
        print(f"{k}: {v}")

    top5 = dashboard.top_directions(programs, n=5)
    print("\n=== Топ-5 направлений ===")
    print(top5.to_string(index=False))

    heatmap_path = output_dir / "heatmap.png"
    dashboard.build_heatmap_static_png(programs, str(heatmap_path))
    top5_path = output_dir / "top_directions.png"
    dashboard.build_top_directions_png(top5, str(top5_path))
    print(f"\nДашборды сохранены: {heatmap_path}, {top5_path}")

    if args.skip_ai:
        print("\n(--skip-ai) Прогноз ИИ пропущен.")
        return

    print("\n=== Прогноз ИИ (OpenAI GPT) ===")
    try:
        forecast = ai_forecast.get_forecast(programs, model=args.model, focus=args.direction)
    except RuntimeError as e:
        print(f"Прогноз не выполнен: {e}")
        return

    print(forecast)
    forecast_path = output_dir / "forecast.txt"
    forecast_path.write_text(forecast, encoding="utf-8")
    print(f"\nПрогноз сохранён: {forecast_path}")


if __name__ == "__main__":
    main()
