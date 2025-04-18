"""change journal table

Revision ID: cb719fbe3a0c
Revises: 423c47845ce6
Create Date: 2025-03-29 10:26:13.162877

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cb719fbe3a0c'
down_revision: Union[str, None] = '423c47845ce6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('journals', sa.Column('soil_number', sa.Integer(), nullable=False))
    op.add_column('journals', sa.Column('water_temperature', sa.BigInteger(), nullable=False))
    op.add_column('journals', sa.Column('air_temperature', sa.BigInteger(), nullable=False))
    op.add_column('journals', sa.Column('air_humidity', sa.BigInteger(), nullable=False))
    op.add_column('journals', sa.Column('light_level', sa.BigInteger(), nullable=False))
    op.add_column('journals', sa.Column('created_at', sa.DateTime(), nullable=False))
    op.add_column('journals', sa.Column('updated_at', sa.DateTime(), nullable=True))
    op.alter_column(
        'journals',
        'date_harvested',
        existing_type=sa.VARCHAR(length=50),
        type_=sa.DateTime(),
        existing_nullable=False,
        postgresql_using="date_harvested::timestamp without time zone"
    )

    op.drop_column('journals', 'temperature')
    op.drop_column('journals', 'number_of_seedbed')
    op.drop_column('journals', 'humidity')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('journals', sa.Column('humidity', sa.BIGINT(), autoincrement=False, nullable=False))
    op.add_column('journals', sa.Column('number_of_seedbed', sa.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('journals', sa.Column('temperature', sa.BIGINT(), autoincrement=False, nullable=False))
    op.alter_column('journals', 'date_harvested',
               existing_type=sa.DateTime(),
               type_=sa.VARCHAR(length=50),
               existing_nullable=False)
    op.drop_column('journals', 'updated_at')
    op.drop_column('journals', 'created_at')
    op.drop_column('journals', 'light_level')
    op.drop_column('journals', 'air_humidity')
    op.drop_column('journals', 'air_temperature')
    op.drop_column('journals', 'water_temperature')
    op.drop_column('journals', 'soil_number')
    # ### end Alembic commands ###
