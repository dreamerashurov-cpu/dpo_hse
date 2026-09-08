import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
# исходный файл ожидается рядом со скриптом, под этим именем
RAW_PATH = BASE_DIR / "programs.xls"

COLUMN_MAP = {
    "Регистрационный номер": "program_id",
    "Кампус НИУ ВШЭ, на базе которого реализуется программа": "campus",
    "Факультет или другое образовательное подразделение, реализующее программу": "department",
    "Область подготовки": "direction",
    "Год начала реализации программы (Осуществлен набор на программу)": "year_start",
    "Реализована в отчетном году": "realized_flag",
    "Объем программы в часах (всего)": "hours",
    "Стоимость программы": "cost",
    "Численность слушателей, прошедших обучение по программе в отчетном году (всего)": "listeners_actual",
    "Плановый набор по всем группам": "listeners_planned",
    "Формат обучения (по способу посещения занятий)": "format",
}


def load_programs() -> pd.DataFrame:
    df = pd.read_excel(RAW_PATH, sheet_name="TDSheet", header=3)
    df = df[list(COLUMN_MAP.keys())].rename(columns=COLUMN_MAP)

    # числа в исходнике — с запятой как десятичным разделителем (рос. локаль)
    for col in ("hours", "cost", "listeners_actual", "listeners_planned"):
        df[col] = (
            df[col].astype(str).str.replace(",", ".", regex=False).str.strip()
        )
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["year_start"] = pd.to_numeric(df["year_start"], errors="coerce")

    missing_mask = df["direction"].isna()
    df["direction"] = df["direction"].astype(str).str.strip()
    df.loc[missing_mask | (df["direction"] == ""), "direction"] = "Не указано"

    return df


if __name__ == "__main__":
    programs = load_programs()
    print(f"Загружено записей: {len(programs)}")
    print(f"Пропуски по направлению: {(programs['direction'] == 'Не указано').sum()}")
    print(f"Уникальных направлений: {programs['direction'].nunique()}")
    print(f"Уникальных кампусов: {programs['campus'].nunique()}")
    programs.to_parquet(BASE_DIR / "programs.parquet", index=False)
    print("Сохранено в programs.parquet")
