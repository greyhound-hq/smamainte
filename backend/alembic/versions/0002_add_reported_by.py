"""add reported_by to inspection_records

Revision ID: 0002_add_reported_by
Revises: 0001_initial
Create Date: 2025-11-25 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0002_add_reported_by'
down_revision = '0001_initial'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('inspection_records', sa.Column('reported_by', sa.String(length=200), nullable=True))


def downgrade():
    op.drop_column('inspection_records', 'reported_by')
