- [Introduction](#introduction) 
- [Project structure](#project_structure) 
  - [Database setup](#database_setup) 
    - [Obstacle types](#obstacle_types) 

## Introduction <a name=introduction>

## Project structure <a name=project_structure>
```
│   .gitignore
│   Pipfile
│   README.md
├───database_setup                   # Scripts, data to setup database
│   ├───data                         # CSV data for dictionary tables (marking, lightng etc.)
│   └───scripts                      # Auxiliary scripts to prepare data for DDL statements/ alembic bulk_insert operations
│       │   obstacle_types.py        # Get unique obsctale types from DOF
│       └───bulk_insert_data         # Output data from obstacle_types.py,
```

## Database setup <a name=database_setup>

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
