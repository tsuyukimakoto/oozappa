"""add cli only flag to jobset

Revision ID: 3479579b9dba
Revises: 
Create Date: 2015-09-21 13:55:39.274883

"""

# revision identifiers, used by Alembic.
revision = '3479579b9dba'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
from sqlalchemy import Column, Integer
import sqlalchemy as sa


def upgrade():
    op.add_column(
        'jobset',
        Column('cli_only', sa.Boolean, server_default="0")
    )
    pass


def downgrade():
    pass
