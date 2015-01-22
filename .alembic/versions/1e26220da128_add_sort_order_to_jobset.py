"""add sort order to jobset

Revision ID: 1e26220da128
Revises: 
Create Date: 2015-01-16 16:50:39.274883

"""

# revision identifiers, used by Alembic.
revision = '1e26220da128'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
from sqlalchemy import Column, Integer
import sqlalchemy as sa


def upgrade():
    op.add_column(
        'jobset',
        Column('sort_order', sa.Integer, server_default="1")
    )
    pass


def downgrade():
    pass
