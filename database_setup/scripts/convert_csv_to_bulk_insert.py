"""
Convert CSV data for dictionary tables (horizontal_acc, lighting etc.) to data consumed by alembic
bulk_insert operation.
"""
import os
from glob import glob

import pandas as pd


def convert_csv_to_bulk_insert_format(data_path: str) -> None:
    """Convert single CSV file to alembic bulk_insert operation format
    :param data_path: directory path to CSVs
    :type data_path: str
    """
    df = pd.read_csv(
        data_path,
        sep=";",
        keep_default_na=False
    )
    values = df.to_dict(orient="records")
    values = [str(row) for row in values]
    str_values = ",\n".join(values)

    output_root_name = os.path.splitext(os.path.basename(data_path))[0]
    with open(os.path.join("bulk_insert_data", f"{output_root_name}.txt"), "w", encoding="utf-8") as f:
        f.write(str_values)


def main():
    """Main loop"""
    data_dir = os.path.join("..", "data", "csv")
    data_paths = glob(fr"{data_dir}\*.csv")
    for data_path in data_paths:
        convert_csv_to_bulk_insert_format(data_path)


if __name__ == "__main__":
    main()
