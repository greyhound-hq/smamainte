"""initial

Revision ID: 0001_initial
Revises: 
Create Date: 2025-11-25 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create equipments table
    op.create_table(
        'equipments',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('model', sa.String(length=200), nullable=True),
        sa.Column('location', sa.String(length=200), nullable=True),
        sa.Column('photo_url', sa.String(length=1000), nullable=True),
        sa.Column('qr_code_url', sa.String(length=1000), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )

    # Create check_templates table
    op.create_table(
        'check_templates',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('equipment_type', sa.String(length=200), nullable=False),
        sa.Column('item_name', sa.String(length=200), nullable=False),
        sa.Column('item_type', sa.String(length=50), nullable=False),
        sa.Column('order_index', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )

    # Create inspection_records table
    op.create_table(
        'inspection_records',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('equipment_id', sa.Integer(), sa.ForeignKey('equipments.id'), nullable=False),
        sa.Column('template_item_id', sa.Integer(), sa.ForeignKey('check_templates.id'), nullable=True),
        sa.Column('status', sa.String(length=10), nullable=True),
        sa.Column('numeric_value', sa.Float(), nullable=True),
        sa.Column('photo_url', sa.String(length=1000), nullable=True),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('email', sa.String(length=200), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False, server_default='worker'),
    )
    op.create_unique_constraint('uq_users_email', 'users', ['email'])


def downgrade():
    op.drop_constraint('uq_users_email', 'users', type_='unique')
    op.drop_table('users')
    op.drop_table('inspection_records')
    op.drop_table('check_templates')
    op.drop_table('equipments')
