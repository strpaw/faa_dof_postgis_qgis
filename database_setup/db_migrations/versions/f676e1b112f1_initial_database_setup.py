"""initial database setup

Revision ID: f676e1b112f1
Revises: 
Create Date: 2023-09-10 22:46:46.754827

"""
import os
from typing import Sequence, Union

from alembic import op
from geoalchemy2.types import Geography
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f676e1b112f1'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

schema = os.environ.get('DB_SCHEMA')


def upgrade() -> None:
    oas = op.create_table(
        'oas',
        sa.Column('code', sa.CHAR(2), primary_key=True),
        sa.Column('name', sa.VARCHAR(50), nullable=False),
        schema=schema
    )

    op.create_table(
        'country',
        sa.Column('oas_code', sa.CHAR(2), primary_key=True),
        sa.Column('boundary', Geography('MultiPolygon', srid=4326), nullable=False),
        sa.ForeignKeyConstraint(
            ['oas_code'], [f'{schema}.oas.code']
        ),
        schema=schema
    )

    op.create_table(
        'us_state',
        sa.Column('oas_code', sa.CHAR(2), primary_key=True),
        sa.Column('boundary', Geography('MultiPolygon', srid=4326), nullable=False),
        sa.ForeignKeyConstraint(
            ['oas_code'], [f'{schema}.oas.code']
        ),
        schema=schema
    )

    verif_status = op.create_table(
        'verif_status',
        sa.Column('code', sa.CHAR(1), primary_key=True),
        sa.Column('description', sa.VARCHAR(20), nullable=False),
        schema=schema
    )

    obstacle_type = op.create_table(
        'obstacle_type',
        sa.Column('id', sa.SMALLINT, primary_key=True, autoincrement=True),
        sa.Column('type', sa.VARCHAR(35), nullable=False),
        schema=schema
    )

    lighting = op.create_table(
        'lighting',
        sa.Column('code', sa.CHAR(1), primary_key=True),
        sa.Column('description', sa.VARCHAR(35), nullable=False),
        schema=schema
    )

    horizontal_acc = op.create_table(
        'horizontal_acc',
        sa.Column('code', sa.SMALLINT, primary_key=True),
        sa.Column('tolerance', sa.NUMERIC(5, 1), nullable=False),
        sa.Column('tolerance_uom', sa.VARCHAR(10), nullable=False),
        schema=schema
    )

    vertical_acc = op.create_table(
        'vertical_acc',
        sa.Column('code', sa.CHAR(1), primary_key=True),
        sa.Column('tolerance', sa.NUMERIC(5, 1), nullable=False),
        sa.Column('tolerance_uom', sa.VARCHAR(10), nullable=False),
        schema=schema
    )

    marking = op.create_table(
        'marking',
        sa.Column('code', sa.CHAR(1), primary_key=True),
        sa.Column('description', sa.VARCHAR(35), nullable=False),
        schema=schema
    )

    action = op.create_table(
        'action',
        sa.Column('code', sa.CHAR(1), primary_key=True),
        sa.Column('action', sa.VARCHAR(30), nullable=False),
        schema=schema
    )

    op.create_table(
        'obstacle',
        sa.Column('oas_code', sa.CHAR(2), nullable=False),
        sa.Column('obst_number', sa.CHAR(6), nullable=False),
        sa.Column('verif_status_code', sa.CHAR(1), nullable=False),
        sa.Column('city', sa.VARCHAR(20), nullable=False),
        sa.Column('type_id', sa.SMALLINT, nullable=False),
        sa.Column('quantity', sa.SMALLINT, nullable=True),
        sa.Column('agl', sa.NUMERIC(5, 2), nullable=False),
        sa.Column('amsl', sa.NUMERIC(7, 2), nullable=True),
        sa.Column('lighting_code', sa.CHAR(1), nullable=False),
        sa.Column('hor_acc_code', sa.SMALLINT, nullable=False),
        sa.Column('vert_acc_code', sa.CHAR(1), nullable=False),
        sa.Column('marking_code', sa.CHAR(1), nullable=False),
        sa.Column('faa_study_number', sa.CHAR(14), nullable=True),
        sa.Column('action_code', sa.CHAR(1), nullable=False),
        sa.Column('julian_date', sa.CHAR(7), nullable=True),
        sa.Column('valid_from', sa.Date, nullable=False),
        sa.Column('valid_to', sa.Date, nullable=True),
        sa.Column('insert_timestamp', sa.DateTime(timezone=False), nullable=False, server_default=sa.func.now()),
        sa.Column('insert_user', sa.CHAR(8), nullable=False, server_default=sa.func.current_user()),
        sa.Column('modification_timestamp', sa.DateTime(timezone=False), nullable=True),
        sa.Column('modification_user', sa.CHAR(8), nullable=True),
        sa.Column('location', Geography('Point', srid=4326), nullable=False),
        sa.PrimaryKeyConstraint('oas_code', 'obst_number'),
        sa.ForeignKeyConstraint(
            ['oas_code'], [f'{schema}.oas.code']
        ),
        sa.ForeignKeyConstraint(
            ['verif_status_code'], [f'{schema}.verif_status.code']
        ),

        sa.ForeignKeyConstraint(
          ['type_id'], [f'{schema}.obstacle_type.id']
        ),
        sa.ForeignKeyConstraint(
            ['lighting_code'], [f'{schema}.lighting.code']
        ),
        sa.ForeignKeyConstraint(
            ['hor_acc_code'], [f'{schema}.horizontal_acc.code']
        ),
        sa.ForeignKeyConstraint(
            ['vert_acc_code'], [f'{schema}.vertical_acc.code']
        ),
        sa.ForeignKeyConstraint(
            ['marking_code'], [f'{schema}.marking.code']
        ),
        sa.ForeignKeyConstraint(
            ['action_code'], [f'{schema}.action.code']
        ),
        schema=schema
    )

    op.bulk_insert(
        oas,
        [
            {'code': '01', 'name': 'Alabama'},
            {'code': '02', 'name': 'Alaska'},
            {'code': '04', 'name': 'Arizona'},
            {'code': '05', 'name': 'Arkansas'},
            {'code': '06', 'name': 'California'},
            {'code': '08', 'name': 'Colorado'},
            {'code': '09', 'name': 'Connecticut'},
            {'code': '10', 'name': 'Delaware'},
            {'code': '11', 'name': 'DC'},
            {'code': '12', 'name': 'Florida'},
            {'code': '13', 'name': 'Georgia'},
            {'code': '15', 'name': 'Hawaii'},
            {'code': '16', 'name': 'Idaho'},
            {'code': '17', 'name': 'Illinois'},
            {'code': '18', 'name': 'Indiana'},
            {'code': '19', 'name': 'Iowa'},
            {'code': '20', 'name': 'Kansas'},
            {'code': '21', 'name': 'Kentucky'},
            {'code': '22', 'name': 'Louisiana'},
            {'code': '23', 'name': 'Maine'},
            {'code': '24', 'name': 'Maryland'},
            {'code': '25', 'name': 'Massachusetts'},
            {'code': '26', 'name': 'Michigan'},
            {'code': '27', 'name': 'Minnesota'},
            {'code': '28', 'name': 'Mississippi'},
            {'code': '29', 'name': 'Missouri'},
            {'code': '30', 'name': 'Montana'},
            {'code': '31', 'name': 'Nebraska'},
            {'code': '32', 'name': 'Nevada'},
            {'code': '33', 'name': 'New Hampshire'},
            {'code': '34', 'name': 'New Jersey '},
            {'code': '35', 'name': 'New Mexico '},
            {'code': '36', 'name': 'New York'},
            {'code': '37', 'name': 'North Carolina '},
            {'code': '38', 'name': 'North Dakota '},
            {'code': '39', 'name': 'Ohio'},
            {'code': '40', 'name': 'Oklahoma'},
            {'code': '41', 'name': 'Oregon'},
            {'code': '42', 'name': 'Pennsylvania '},
            {'code': '44', 'name': 'Rhode Island '},
            {'code': '45', 'name': 'South Carolina '},
            {'code': '46', 'name': 'South Dakota '},
            {'code': '47', 'name': 'Tennessee'},
            {'code': '48', 'name': 'Texas'},
            {'code': '49', 'name': 'Utah'},
            {'code': '50', 'name': 'Vermont'},
            {'code': '51', 'name': 'Virginia'},
            {'code': '53', 'name': 'Washington '},
            {'code': '54', 'name': 'West Virginia '},
            {'code': '55', 'name': 'Wisconsin'},
            {'code': '56', 'name': 'Wyoming'},
            {'code': 'CA', 'name': 'Canada'},
            {'code': 'MX', 'name': 'Mexico'},
            {'code': 'PR', 'name': 'Puerto Rico'},
            {'code': 'BS', 'name': 'Bahamas'},
            {'code': 'AG', 'name': 'Antigua and Barbuda'},
            {'code': 'AI', 'name': 'Anguilla'},
            {'code': 'NL', 'name': 'Netherlands Antilles (formerly AN)'},
            {'code': 'AW', 'name': 'Aruba'},
            {'code': 'CU', 'name': 'Cuba'},
            {'code': 'DM', 'name': 'Dominica'},
            {'code': 'DO', 'name': 'Dominican Republic'},
            {'code': 'GP', 'name': 'Guadeloupe'},
            {'code': 'HN', 'name': 'Honduras'},
            {'code': 'HT', 'name': 'Haiti'},
            {'code': 'JM', 'name': 'Jamaica'},
            {'code': 'KN', 'name': 'St. Kitts and Nevis'},
            {'code': 'KY', 'name': 'Cayman Islands'},
            {'code': 'LC', 'name': 'Saint Lucia'},
            {'code': 'MQ', 'name': 'Martinique'},
            {'code': 'MS', 'name': 'Montserrat'},
            {'code': 'TC', 'name': 'Turks and Caicos Islands'},
            {'code': 'VG', 'name': 'British Virgin Islands'},
            {'code': 'VI', 'name': 'Virgin Islands'},
            {'code': 'AS', 'name': 'American Samoa'},
            {'code': 'FM', 'name': 'Federated States of Micronesia'},
            {'code': 'GU', 'name': 'Guam '},
            {'code': 'KI', 'name': 'Kiribati'},
            {'code': 'MH', 'name': 'Marshall Islands'},
            {'code': 'QM', 'name': 'Midway Islands (formerly MI) '},
            {'code': 'MP', 'name': 'Northern Mariana Islands'},
            {'code': 'PW', 'name': 'Palau '},
            {'code': 'RU', 'name': 'Russia '},
            {'code': 'TK', 'name': 'Tokelau'},
            {'code': 'QW', 'name': 'Wake Island (formerly WQ) '},
            {'code': 'WS', 'name': 'Samoa'},
            {'code': 'US', 'name': 'USA'}
        ]
    )

    op.bulk_insert(
        verif_status,
        [
            {'code': 'O', 'description': 'verified'},
            {'code': 'U', 'description': 'unverified'}
        ]
    )

    op.bulk_insert(
        obstacle_type,
        [
            {"type": "AG EQUIP"},
            {"type": "AMUSEMENT PARK"},
            {"type": "ANTENNA"},
            {"type": "ARCH"},
            {"type": "BALLOON"},
            {"type": "BLDG"},
            {"type": "BLDG-TWR"},
            {"type": "BRIDGE"},
            {"type": "CATENARY"},
            {"type": "COOL TWR"},
            {"type": "CRANE"},
            {"type": "CTRL TWR"},
            {"type": "DAM"},
            {"type": "DOME"},
            {"type": "ELEC SYS"},
            {"type": "ELEVATOR"},
            {"type": "FENCE"},
            {"type": "GATE"},
            {"type": "GEN UTIL"},
            {"type": "GRAIN ELEVATOR"},
            {"type": "HANGAR"},
            {"type": "HEAT COOL SYSTEM"},
            {"type": "LANDFILL"},
            {"type": "LGTHOUSE"},
            {"type": "MET"},
            {"type": "MONUMENT"},
            {"type": "NATURAL GAS SYSTEM"},
            {"type": "NAVAID"},
            {"type": "PIPELINE PIPE"},
            {"type": "PLANT"},
            {"type": "POLE"},
            {"type": "POWER PLANT"},
            {"type": "REFINERY"},
            {"type": "RIG"},
            {"type": "SHIP"},
            {"type": "SIGN"},
            {"type": "SILO"},
            {"type": "SOLAR PANELS"},
            {"type": "SPIRE"},
            {"type": "STACK"},
            {"type": "STADIUM"},
            {"type": "T-L TWR"},
            {"type": "TANK"},
            {"type": "TOWER"},
            {"type": "TRAMWAY"},
            {"type": "UTILITY POLE"},
            {"type": "VERTICAL STRUCTURE"},
            {"type": "WALL"},
            {"type": "WIND INDICATOR"},
            {"type": "WINDMILL"},
            {"type": "WINDSOCK"}
        ]
    )

    op.bulk_insert(
        lighting,
        [
            {'code': 'R', 'description': 'Red'},
            {'code': 'D', 'description': 'Medium intensity White Strobe & Red'},
            {'code': 'H', 'description': 'High Intensity White Strobe & Red'},
            {'code': 'M', 'description': 'Medium Intensity White Strobe'},
            {'code': 'S', 'description': 'High Intensity White Strobe'},
            {'code': 'F', 'description': 'Flood'},
            {'code': 'C', 'description': 'Dual Medium Catenary'},
            {'code': 'W', 'description': 'Synchronized Red Lighting'},
            {'code': 'L', 'description': 'Lighted (Type Unknown)'},
            {'code': 'N', 'description': 'None'},
            {'code': 'U', 'description': 'Unknown'}
        ]
    )

    op.bulk_insert(
        horizontal_acc,
        [
            {'code': 1, 'tolerance': 20.0, 'tolerance_uom': 'ft'},
            {'code': 2, 'tolerance': 50.0, 'tolerance_uom': 'ft'},
            {'code': 3, 'tolerance': 100.0, 'tolerance_uom': 'ft'},
            {'code': 4, 'tolerance': 250.0, 'tolerance_uom': 'ft'},
            {'code': 5, 'tolerance': 500.0, 'tolerance_uom': 'ft'},
            {'code': 6, 'tolerance': 1000.0, 'tolerance_uom': 'ft'},
            {'code': 7, 'tolerance': 0.5, 'tolerance_uom': 'NM'},
            {'code': 8, 'tolerance': 1.0, 'tolerance_uom': 'NM'},
            {'code': 9, 'tolerance': -999.0, 'tolerance_uom': 'NA'}
        ]
    )

    op.bulk_insert(
        vertical_acc,
        [
            {'code': 'A', 'tolerance': 3, 'tolerance_uom': 'ft'},
            {'code': 'B', 'tolerance': 10, 'tolerance_uom': 'ft'},
            {'code': 'C', 'tolerance': 20, 'tolerance_uom': 'ft'},
            {'code': 'D', 'tolerance': 50, 'tolerance_uom': 'ft'},
            {'code': 'E', 'tolerance': 125, 'tolerance_uom': 'ft'},
            {'code': 'F', 'tolerance': 250, 'tolerance_uom': 'ft'},
            {'code': 'G', 'tolerance': 500, 'tolerance_uom': 'ft'},
            {'code': 'H', 'tolerance': 1000, 'tolerance_uom': 'ft'},
            {'code': 'I', 'tolerance': -999, 'tolerance_uom': 'NA'}
        ]
    )

    op.bulk_insert(
        marking,
        [
            {'code': 'P', 'description': 'Orange or Orange and White Paint'},
            {'code': 'W', 'description': 'White Paint Only'},
            {'code': 'M', 'description': 'Marked'},
            {'code': 'F', 'description': 'Flag Marker'},
            {'code': 'S', 'description': 'Spherical Marker'},
            {'code': 'N', 'description': 'None'},
            {'code': 'U', 'description': 'Unknown'}
        ]
    )

    op.bulk_insert(
        action,
        [
            {'code': 'A', 'action': 'Add'},
            {'code': 'C', 'action': 'Change'}
        ]
    )


def downgrade() -> None:
    pass
