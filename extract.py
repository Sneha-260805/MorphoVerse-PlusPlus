import json
import math
import os
import re
from pathlib import Path

import pandas as pd


EXCEL_FILE = "MorphoVerse_PlusPlus_FINAL_v3.xlsx"
DATA_SHEET = "MorphoVerse++"
OUTPUT_FOLDER = "files"

LANGUAGE_POEMS = {
    "Hindi": ["MV++_0232", "MV++_0108", "MV++_0495"],
    "Kannada": ["MV++_0982", "MV++_1005", "MV++_0952"],
    "Konkani": ["MV++_1168", "MV++_1167", "MV++_1169"],
    "Malayalam": ["MV++_1177", "MV++_1183", "MV++_1176"],
    "Manipuri": ["MV++_1184", "MV++_1185", "MV++_1187"],
    "Rajasthani": ["MV++_1229", "MV++_1231", "MV++_1232"],
    "Santhali": ["MV++_1238", "MV++_1237", "MV++_1239"],
    "Sindhi": ["MV++_1243", "MV++_1244", "MV++_1246"],
    "Odia": ["MV++_1200", "MV++_1201", "MV++_1206"],
}


def clean_column_name(column_name):
    return (
        str(column_name)
        .strip()
        .replace("\n", " ")
    )


def to_snake_case(column_name):
    name = clean_column_name(column_name).lower()
    name = re.sub(r"[^a-z0-9]+", "_", name)
    return name.strip("_")


def json_safe_value(value):
    if value is None:
        return None

    if isinstance(value, float) and math.isnan(value):
        return None

    if pd.isna(value):
        return None

    if hasattr(value, "item"):
        value = value.item()

    if isinstance(value, str):
        value = value.strip()

        if not value:
            return None

        if value[0] in "[{":
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value

        return value

    return value


def load_poem_sheet(excel_file):
    df = pd.read_excel(
        excel_file,
        sheet_name=DATA_SHEET,
        header=1,
    )

    df.columns = [clean_column_name(column) for column in df.columns]
    df = df.dropna(how="all")
    df["Poem ID"] = df["Poem ID"].astype(str).str.strip()

    return df


def row_to_poem_record(row):
    record = {}

    for column, value in row.items():
        record[to_snake_case(column)] = json_safe_value(value)

    return record


def main():
    df = load_poem_sheet(EXCEL_FILE)
    output_root = Path(OUTPUT_FOLDER)
    output_root.mkdir(parents=True, exist_ok=True)

    poems_by_id = {
        str(row["Poem ID"]).strip(): row
        for _, row in df.iterrows()
    }

    missing_poems = []

    for language, poem_ids in LANGUAGE_POEMS.items():
        language_records = []

        for poem_id in poem_ids:
            row = poems_by_id.get(poem_id)

            if row is None:
                missing_poems.append((language, poem_id))
                continue

            record = row_to_poem_record(row)
            record["assigned_language"] = language
            language_records.append(record)

        output_file = output_root / f"{language}.json"
        with output_file.open("w", encoding="utf-8") as f:
            json.dump(language_records, f, ensure_ascii=False, indent=2)

        print(f"{language}: {len(language_records)}/{len(poem_ids)} poems saved")

    if missing_poems:
        print("\nMissing poem IDs:")
        for language, poem_id in missing_poems:
            print(f"- {language}: {poem_id}")

    print(f"\nDONE. Files written to: {output_root.resolve()}")


if __name__ == "__main__":
    main()
