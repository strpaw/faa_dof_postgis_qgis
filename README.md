- [Introduction](#introduction) 
- [Project structure](#project_structure) 
  - [Database setup](#database_setup) 
    - [Dictionary tables (without obstacle types)](#dictionary_tables)
    - [Obstacle types](#obstacle_types) 

## Introduction <a name=introduction>

## Project structure <a name=project_structure>
```
│   .gitignore
│   Pipfile
│   README.md
├───database_setup                                # Scripts, data to setup database
│   ├───data                                      # Data for dictionary tables
│   │   └───csv                                   # CSV data for dictionary tables (marking, lightng etc.)
│   │           horizontal_acc.csv
│   │           lighting.csv
│   │           marking.csv
│   │           obstacle_type.csv
│   │           verif_status.csv
│   │           vertical_acc.csv
│   └───scripts                                   # Auxiliary scripts to prepare data for DDL statements/ alembic bulk_insert operations
│       │   convert_csv_to_bulkt_insert.py        # Generate content for alembic bulk_insert operations
│       │   obstacle_types.py                     # Get unique obsctale types from DOF
│       └───bulk_insert_data                      # Output data from obstacle_types.py,
```

## Database setup <a name=database_setup>

### Dictionary tables (without obstacle types) <a name=dictionary_tables>

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

### Obstacle types <a name=obstacle_types>

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
