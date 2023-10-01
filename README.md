- [Introduction](#introduction) 
- [Project structure](#project_structure)
- [Environment setup](#env_setup)
- [Database setup](#database_setup)
  - [Setup with alembic](#setup_alembic)
  - [Auxiliary scripts](#aux_scripts)
    - [convert_csv_to_bulk_insert.py](#dictionary_tables)
    - [load_countries_states.py](#load_ctry_states)
    - [obstacle_types.py](#obstacle_types)
    - [usa_state_oas.py](#usa_state_oas)



## Introduction <a name=introduction>

Database (PostgreSQL+PostGIS) and QGIS Plugin to store and manage obstacles published by Federal Aviation Administration (FAA)
in the Digital Obstacle File (DOF) format.
For more information please refer [here](https://www.faa.gov/air_traffic/flight_info/aeronav/digital_products/dof/)

## Project structure <a name=project_structure>

Note:
- All files are not shown for the sake of clarity
- Skipped files: database alembic version scripts

```
faa_dof_postgis_qgis                              # Main project directory
│   .gitignore
│   Pipfile
│   README.md
└───database_setup                                # Scripts, data to setup database
    │   .env                                      # Database admin credentials (edit with custom credentials)
    │   alembic.ini
    ├───data                                      # Data for dictionary tables
    │   └───csv                                   # CSV data for dictionary tables (marking, lightng etc.)
    |           action.csv
    │           horizontal_acc.csv
    │           lighting.csv
    │           marking.csv
    │           oas.csv
    │           obstacle_type.csv
    │           verif_status.csv
    │           vertical_acc.csv
    ├───db_migrations
    │   │   env.py
    │   │   README
    │   │   script.py.mako
    │   └───versions
    └───scripts                                   # Auxiliary scripts to prepare data for DDL statements/ alembic bulk_insert operations
        │   convert_csv_to_bulk_insert.py         # Generate content for alembic bulk_insert operations
        │   load_countries_states.py              # Load spatial data (counries, states) to database
        │   obstacle_types.py                     # Get unique obsctale types from DOF
        │   scripts_config.yml                    # Configuration file for scripts
        │   usa_state_oas.py                      # Get country/state - oas code pairs
        └───bulk_insert_data                      # Output data from obstacle_types.py,
```

## Environment setup <a name=env_setup>

Notes:
 - needed in case database tables are created with alembic
 
Steps:
1. Install pipenv: `pip install pipenv`
2. `cd <main project directory>`
3. `pipenv shell`
4. `pipenv install`

## Database setup <a name=database_setup>

## Setup with alembic <a name=setup_alembic>

1. Edit file `<main project dir>\database_setup>.env` (admin credentials to target database)
2. `cd <main project dir>\database_setup`
3. Run `alembic upgrade head`
4. Load countries, states spatial data. See [load_countries_states.py](#load_ctry_states)

### Auxiliary scripts <a name=aux_scripts>

#### convert_csv_to_bulk_insert.py <a name=dictionary_tables>

##### Purpose
Generate input into alembic bulk_insert operations
Notes 
- Input is taken from: `<main project dir>\database_setutp\data\csv`
- Output is saved in: `<main project dir>\database_setutp\scripts\bulk_insert_data`

#### Usage
1. `cd <main project dir>\database_setup\scripts`
2. `python convert_csv_to_bulk_insert.py`

#### Input

Example input (part of a file):

    code;tolerance;tolerance_uom
    1;20;ft
    2;50;ft

#### Output
Example output (part of a file):

    {'code': 1, 'tolerance': 20.0, 'tolerance_uom': 'ft'},
    {'code': 2, 'tolerance': 50.0, 'tolerance_uom': 'ft'},
    {'code': 3, 'tolerance': 100.0, 'tolerance_uom': 'ft'},

#### load_countries_states.py <a name=load_ctry_states>

##### Purpose
Script to load spatial data (countries, USA states) to database.

##### Input

Spatial data with countries, usa states boundaries - supported by GeoPandas.

##### Output

FAA DOF database.

##### Usage

1. `cd <main project dir>\database_setup\scripts`
2. Edit `scripts_config.yml`, sections: 
   1. `database`
   2. `load_countries_states`
3. Run `python load_countries_states.py`

#### obstacle_types.py <a name=obstacle_types>

##### Purpose

Generate input into alembic bulk_insert operations - obstacle_types table based on DOF file.

Notes
- Refer to the Digital Obstacle File (DOF) documentation for file format specification   
  for input parameters
- before running the script: `cd database_setup/scripts`
- output is saved to `bulk_insert_data/obstacle_types.txt`

##### Usage 

```
python obstacle_types.py [-h]
                      -i, --input
                      Path to the input DOF from which unique obstacle types will be taken
                      
                      -r, --skip-rows
                      Number of rows to skip to load obstacle data (header lines)
                      
                      -f, --from-column
                      Number of the column where obstacle type begins
                      
                      -t, --to-column
                      Number of the column where obstacle type ends
                      
                      -e, --encoding
                      Input file encoding
```
##### Input 

DOF data (example DOF.DAT)

##### Output
Example output (part of output file): 

    {"type": "AG EQUIP"},
    {"type": "AMUSEMENT PARK"},
    {"type": "ANTENNA"},
    {"type": "ARCH"},
    {"type": "BALLOON"},

#### usa_state_oas.py <a name=usa_state_oas>

##### Purpose
Script to generate pairs USA state code (example AK for Alaska) and OAS code ("02").

##### Output

File `usa_state_oas_code.txt` in the directory from which script is executed.
Example:

    AL: "01"
    AK: "02"
    AZ: "04"
    AR: "05"

##### Usage

1. `cd <main project dir>\database_setup\scripts`
2. Edit `scripts_config.yml`, section `usa_state_oas`
3. Run `python usa_state_oas.py`
