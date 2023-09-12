- [Introduction](#introduction) 
- [Project structure](#project_structure)
  - [Database setup](#database_setup)
     - [Setup with alembic](#setup_alembic)
     - [Auxiliary scripts](#aux_scripts)
       - [Dictionary tables (without obstacle types)](#dictionary_tables)
       - [Obstacle types](#obstacle_types) 
       - [usa_state_oas.py](#usa_state_oas)



## Introduction <a name=introduction>

## Project structure <a name=project_structure>

Note:
- All files are not shown for the sake of clarity
- Skipped files: database alembic version scripts

```
│   .gitignore
│   Pipfile
│   README.md
├───database_setup                                # Scripts, data to setup database
│   │   .env                                      # Database admin credentials (edit with custom credentials)
│   │   alembic.ini
│   ├───data                                      # Data for dictionary tables
│   │   └───csv                                   # CSV data for dictionary tables (marking, lightng etc.)
│   │           horizontal_acc.csv
│   │           lighting.csv
│   │           marking.csv
│   │           obstacle_type.csv
│   │           verif_status.csv
│   │           vertical_acc.csv
│   ├───db_migrations
│   │   │   env.py
│   │   │   README
│   │   │   script.py.mako
│   │   └───versions
│   └───scripts                                   # Auxiliary scripts to prepare data for DDL statements/ alembic bulk_insert operations
│       │   convert_csv_to_bulkt_insert.py        # Generate content for alembic bulk_insert operations
│       │   obstacle_types.py                     # Get unique obsctale types from DOF
│       │   usa_state_oas.py
│       └───bulk_insert_data                      # Output data from obstacle_types.py,
```

## Database setup <a name=database_setup>

## Setup with alembic <a name setup_alembic>

1. Edit file `<main project dir>\database_setup>.env` (admin credentials to target database)
2. `cd <main project dir>\database_setup`
3. Run `alembic upgrade head`

### Auxiliary scripts <a name aux_scripts>

#### Dictionary tables (without obstacle types) <a name=dictionary_tables>

Notes
- Script `convert_csv_to_bulkt_insert.py` used to generate input into alembic bulk_insert operations
- Before running the script: `cd <main project dir>\database_setup\scripts`
- Input is taken from: `<main project dir>\database_setutp\data\csv`
- Output is saved in: `<main project dir>\database_setutp\scripts\bulk_insert_data`

Usage:  
`python convert_csv_to_bulkt_insert.py`

Example input (part of a file):

    code;tolerance;tolerance_uom
    1;20;ft
    2;50;ft

Example output (part of a file):

    {'code': 1, 'tolerance': 20.0, 'tolerance_uom': 'ft'},
    {'code': 2, 'tolerance': 50.0, 'tolerance_uom': 'ft'},
    {'code': 3, 'tolerance': 100.0, 'tolerance_uom': 'ft'},

#### Obstacle types <a name=obstacle_types>

Notes
- Script used to generate input into alembic bulk_insert operations
- Refer to the Digital Obstacle File (DOF) documentation for file format specification   
  for input parameters
- before runnning the script: `cd database_setup/scripts`
- output is saved to `bulk_insert_data/obstacle_types.txt`

Usage:
```
python obstacle_types [-h]
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
