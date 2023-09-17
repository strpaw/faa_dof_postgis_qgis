"""Script to load countries and USA states spatial data into database"""
import geopandas as gpd
import sqlalchemy
from yaml import safe_load
from sqlalchemy import create_engine, text


class Configuration:
    """Keep application configuration"""

    def __init__(self, config_path: str = "scripts_config.yml") -> None:
        """
        :param config_path: path to the configuration file
        :type config_path: str
        """
        with open(config_path, "r", encoding="utf-8") as f:
            content = safe_load(f)
            self.db_credentials = content["database"]["credentials"]
            """Database credentials"""

            country_cfg = content["load_countries_states"]["countries"]
            self.ctry_input_path = country_cfg["input_file"]
            """Path to the file with countries spatial data"""
            self.country_column = country_cfg["column"]
            """Column that holds country code"""
            self.country_codes_map = country_cfg["input_dof_map"]
            """Rules between source data country codes and codes used in DOF data (OAS code)"""

            usa_states_cfg = content["load_countries_states"]["usa_states"]
            self.states_input_path = usa_states_cfg["input_file"]
            """Path to the file with USA states spatial data"""
            self.states_ctry_column = usa_states_cfg["ctry_column"]
            """Column that holds country code. (
            Note: Assumption that the input data file covers all countries and their administration division, 
            example: Natural Earth data"""
            self.state_column = usa_states_cfg["state_column"]
            """Column that holds state code"""
            self.state_codes_map = usa_states_cfg["input_dof_map"]
            """Rules between source data states codes and codes used in DOF data (OAS code)"""


def get_countries(
        input_path: str,
        code_column: str,
        countries: list[str]
) -> gpd.GeoDataFrame:
    """Return country data (geometry, attributes) - only for countries that are used in DOF
    :param input_path: path to the source file with country data
    :type input_path: str
    :param code_column: column name with country codes
    :type code_column: str
    :param countries: countries (used in DOF), codes as in source file
    :type countries: list
    :return: countries data (used in DOF)
    :rtype: geopandas.GeoDataFrame
    """
    gdf = gpd.read_file(
        input_path,
        include_fields=[code_column]
    )
    return gdf.loc[gdf[code_column].isin(countries)]


def get_usa_states(
        input_path: str,
        ctry_field: str,
        state_field: str,
):
    """Return states data (geometry, codes).
    :param input_path: path to input data file
    :type input_path: str
    :param ctry_field: column name used for country code
    :type ctry_field: str
    :param state_field: column name used for state code
    :type state_field: str
    :return: states data
    :rtype: geopandas.GeoDataFrame
    """
    gdf = gpd.read_file(
        input_path,
        include_fields=[ctry_field, state_field]
    )
    gdf = gdf.loc[gdf[ctry_field] == "USA"]
    gdf.drop(columns=[ctry_field], inplace=True)
    return gdf


def prepare_data(
        gdf: gpd.GeoDataFrame,
        src_code_column: str,
        src_target_map: dict[str, str]
) -> gpd.GeoDataFrame:
    """Return data the database tables country, usa_state.
    :param gdf: Data to be converted to a form compatible with the database tables country, usa_state
    :type gdf: geopandas.GeoDataFrame
    :param src_code_column: Column name with country/state codes
    :type src_code_column: str
    :param src_target_map: Map between source country/state codes and DOF country/state codes
    :type src_target_map: dict[str, str]
    :return:
    :rtype: geopandas.GeoDataFrame
    """
    gdf.loc[:, ["oas_code"]] = gdf[src_code_column].apply(lambda row: src_target_map[row])
    gdf.drop(columns=[src_code_column], inplace=True)
    gdf.rename(columns={"geometry": "boundary"}, inplace=True)
    gdf.set_geometry("boundary", inplace=True)
    return gdf


def load_data(
        gdf: gpd.GeoDataFrame,
        target_table: str,
        engine: sqlalchemy.engine.Engine
):
    """Load prepared data to database.
    :param gdf: Data to be loaded
    :type gdf: geopandas.GeoDataFrame
    :param target_table: table name to which daa will be loaded
    :type target_table: str
    :param engine: SQLAlchemy engine
    :type engine: sqlalchemy.engine.Engine
    """
    # Some geometries fetched from source data might be a Polygon type, ensure all are MultiPolygons (ST_Multi)
    query_copy = f"""insert into dof.{target_table} (oas_code, boundary)
                select 
                    oas_code,
                    ST_Multi(boundary)::geography
                from dof.{target_table}_tmp;"""
    query_drop = f"drop table if exists dof.{target_table}_tmp;"

    with engine.connect() as con:
        con.execution_options(isolation_level="AUTOCOMMIT")
        gdf.to_postgis(
            name=f"{target_table}_tmp",
            con=con,
            if_exists="append",
            schema="dof",
            index=False,
        )
        con.execute(text(query_copy))
        con.execute(text(query_drop))


def load_countries(
        config: Configuration,
        engine: sqlalchemy.engine.Engine
) -> None:
    """Load countries boundaries from shp to database.
    :param config: application configuration
    :type config: Configuration
    :param engine: SQLAlchemy engine
    :type engine: sqlalchemy.engine.Engine
    """
    countries = get_countries(
        input_path=config.ctry_input_path,
        code_column=config.country_column,
        countries=config.country_codes_map.keys()
    )

    data = prepare_data(
        gdf=countries,
        src_code_column=config.country_column,
        src_target_map=config.country_codes_map
    )

    load_data(
        gdf=data,
        target_table="country",
        engine=engine
    )


def load_states(
        config: Configuration,
        engine: sqlalchemy.engine.Engine
) -> None:
    """Load USA states boundaries from shp to database.
    :param config: application configuration
    :type config: Configuration
    :param engine: SQLAlchemy engine
    :type engine: sqlalchemy.engine.Engine
    """
    states = get_usa_states(
        input_path=config.states_input_path,
        ctry_field=config.states_ctry_column,
        state_field=config.state_column
    )

    data = prepare_data(
        gdf=states,
        src_code_column=config.state_column,
        src_target_map=config.state_codes_map
    )

    load_data(
        gdf=data,
        target_table="us_state",
        engine=engine
    )


def main():
    config = Configuration()
    engine = create_engine("postgresql+psycopg2://{user}:{password}@{host}:5432/{name}".format(**config.db_credentials))
    load_countries(config, engine)
    load_states(config, engine)


if __name__ == "__main__":
    main()
