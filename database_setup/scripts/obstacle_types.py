"""
Parse DOF file to fetch unique obstacle types.
Save result into file obstacle_types.txt with format accepted by alembic bulk_insert operation (list of dicts)
example:
{"type": "UTILITY POLE"},
{"type": "VERTICAL STRUCTURE"},
{"type": "WINDSOCK"}
"""
import argparse
import sys

import pandas as pd


def parse_args() -> argparse.Namespace:
    """Parse input arguments"""
    parser = argparse.ArgumentParser(
        prog="Obstacle types",
        description="Fetch unique obstacle types from DOF (Digital Obstacle File)"
    )

    parser.add_argument(
        "-i",
        "--input-file",
        type=str,
        required=True,
        help="path to the input DOF"
    )
    parser.add_argument(
        "-r",
        "--skip-rows",
        type=int,
        required=True,
        help="Number of rows to skip to load obstacle data (header lines)"
    )

    parser.add_argument(
        "-f",
        "--from-column",
        type=int,
        required=True,
        help="Number of the column where obstacle type begins"
    )

    parser.add_argument(
        "-t",
        "--to-column",
        type=int,
        required=True,
        help="Number of the column where obstacle type ends"
    )

    parser.add_argument(
        "-e",
        "--encoding",
        type=str,
        required=True,
        help="Input file encoding"
    )

    return parser.parse_args()


def get_obstacle_types(
        file_path: str,
        skip_rows: int,
        from_column: int,
        to_column: int,
        encoding: str
) -> pd.Series:
    """Return unique obstacle types based on the Digital Obstacle File (DOF).
    :param file_path: path to DOF data file
    :type file_path: str
    :param skip_rows: number of header rows to skip
    :type skip_rows: int
    :param from_column: number of the column where obstacle type begins
    :type from_column: int
    :param to_column: number of the column where obstacle type ends
    :type to_column: int
    :param encoding: input file encoding
    :type encoding: str
    :return: Unique obstacle types
    :rtype: pd.Series
    """
    df = pd.read_fwf(
        file_path,
        skiprows=skip_rows,
        header=None,
        colspecs=[(from_column, to_column)],
        names=["description"],
        encoding=encoding
    )

    types = pd.DataFrame(
        df["description"].unique(),
        columns=["description"]
    )

    types.sort_values(
        by=["description"],
        axis=0,
        inplace=True
    )

    return types.description.str.strip()


def main() -> None:
    """Main loop"""
    args = parse_args()
    try:
        obst_types = get_obstacle_types(
            file_path=args.input_file,
            skip_rows=args.skip_rows,
            from_column=args.from_column,
            to_column=args.to_column,
            encoding=args.encoding
        )
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    values = []
    for _, value in obst_types.items():
        values.append('{"type": ' + f'"{value}"' + "}")

    str_values = ",\n".join(values)

    with open(r"bulk_insert_data\obstacle_types.txt", "w", encoding="utf-8") as f:
        f.write(str_values)


if __name__ == "__main__":
    main()
