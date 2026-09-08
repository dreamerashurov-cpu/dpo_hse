from __future__ import annotations

from pathlib import Path
import os
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_MODEL = "gpt-4o-mini"


def aggregate_trend(programs: pd.DataFrame, top_n: int = 25) -> pd.DataFrame:
    grouped = (
        programs.groupby(["direction", "campus", "year_start"], dropna=False)
        .size()
        .reset_index(name="n_programs")
    )
    totals = (
        grouped.groupby(["direction", "campus"])["n_programs"]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
        .index
    )
    subset = grouped.set_index(["direction", "campus"]).loc[list(totals)].reset_index()

    pivot = subset.pivot_table(
        index=["direction", "campus"], columns="year_start", values="n_programs", fill_value=0
    )
    pivot.columns = [str(int(c)) for c in pivot.columns]
    pivot["total"] = pivot.sum(axis=1)
    pivot = pivot.sort_values("total", ascending=False).reset_index()
    return pivot


def format_trend_for_prompt(trend: pd.DataFrame) -> str:
    year_cols = [c for c in trend.columns if c not in ("direction", "campus", "total")]
    lines = ["direction | campus | " + " | ".join(year_cols) + " | total"]
    for _, row in trend.iterrows():
        values = " | ".join(str(int(row[c])) for c in year_cols)
        lines.append(f"{row['direction']} | {row['campus']} | {values} | {int(row['total'])}")
    return "\n".join(lines)


def build_messages(trend_text: str, stats: dict, focus: str | None = None) -> list[dict]:
    system = (
        "Ты аналитик дополнительного профессионального образования (ДПО) НИУ ВШЭ. "
        "Тебе дана реальная историческая таблица числа запущенных программ по "
        "направлению подготовки, кампусу и году (2019-2026). Реальных данных по "
        "спросу нет — оценивай будущий год ТОЛЬКО по тренду предложения "
        "(рост/падение/стабильность числа программ по годам), явно указывая, что "
        "это прогноз на основе тренда, а не подтверждённого спроса."
    )
    focus_instruction = (
        f"\nОсобое внимание удели направлению «{focus}», но не игнорируй общую картину."
        if focus
        else ""
    )
    user = (
        f"Общая сводка: {stats}\n\n"
        f"Историческая таблица (топ направлений и кампусов по объёму, число программ по годам):\n"
        f"{trend_text}\n\n"
        "Составь прогноз на следующий год после последнего в таблице.\n"
        "Формат ответа:\n"
        "1) Таблица: направление | кампус | рекомендуемое количество программ | обоснование (1 фраза).\n"
        "2) Краткое резюме (3-5 предложений): общие тенденции и риски прогноза."
        f"{focus_instruction}"
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def get_forecast(
    programs: pd.DataFrame,
    model: str = DEFAULT_MODEL,
    focus: str | None = None,
    top_n: int = 25,
) -> str:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Не задана переменная окружения OPENAI_API_KEY. "
            "Задайте её перед запуском: export OPENAI_API_KEY=sk-..."
        )

    from openai import OpenAI
    from dashboard import summary_stats

    trend = aggregate_trend(programs, top_n=top_n)
    trend_text = format_trend_for_prompt(trend)
    stats = summary_stats(programs)
    messages = build_messages(trend_text, stats, focus=focus)

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(model=model, messages=messages)
    return response.choices[0].message.content


if __name__ == "__main__":
    programs = pd.read_parquet(BASE_DIR / "programs.parquet")
    forecast = get_forecast(programs)
    print(forecast)
