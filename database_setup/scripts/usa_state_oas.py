"""Generate pairs USA state code and corresponding oas code, example: AL: "01" """
import pandas as pd
from yaml import safe_load
import sys

from typing import NamedTuple


class Attribute(NamedTuple):
    """Keep attribute column ranges"""
    col_from: int
    col_to: int


class Configuration:
    """Keep application configuration"""
    def __init__(self, config_path: str = "scripts_config.yml") -> None:
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = safe_load(f)
                config = config["usa_state_oas"]
                self.file_path: str = config["file_path"]
                """Input DOF path"""
                self.skip_rows: int = config["skip_rows"]
                self.oas_code: Attribute = Attribute(**config["oas_code"])
                """Output name for attribute keeping oas code"""
                self.ctry_code: Attribute = Attribute(**config["ctry_code"])
                """Output name for attribute keeping country code"""
                self.encoding: str = config["encoding"]
                """Input DOF encoding"""
        except Exception as e:
            print(e)
            sys.exit(1)


def main():
    config = Configuration()
    df = pd.read_fwf(
        filepath_or_buffer=config.file_path,
        skiprows=config.skip_rows,
        header=None,
        colspecs=[
            (config.oas_code.col_from, config.oas_code.col_to),
            (config.ctry_code.col_from, config.ctry_code.col_to)],
        names=["oas_code", "ctry_code"],
        encoding=config.encoding
    )
    df.drop_duplicates(inplace=True)
    df.dropna(inplace=True)
    with open("usa_state_oas_code.txt", "w") as f:
        for _, row in df.iterrows():
            f.write(f"""{row['ctry_code']}: "{row['oas_code']}"\n""")


if __name__ == "__main__":
    main()
