"""Initial migration - customer_sessions table

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create customer_sessions table
    op.create_table('customer_sessions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('customer', sa.String(length=255), nullable=False),
    sa.Column('region', sa.String(length=100), nullable=False),
    sa.Column('sessions', sa.Integer(), nullable=False),
    sa.Column('source', sa.String(length=255), nullable=False),
    sa.Column('destination', sa.String(length=255), nullable=False),
    sa.Column('time_consumed', sa.Integer(), nullable=True),
    sa.Column('observation', sa.Text(), nullable=True),
    sa.Column('uploaded_at', sa.DateTime(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # Create indexes
    op.create_index(op.f('ix_customer_sessions_customer'), 'customer_sessions', ['customer'], unique=False)
    op.create_index(op.f('ix_customer_sessions_region'), 'customer_sessions', ['region'], unique=False)
    op.create_index(op.f('ix_customer_sessions_source'), 'customer_sessions', ['source'], unique=False)
    op.create_index(op.f('ix_customer_sessions_destination'), 'customer_sessions', ['destination'], unique=False)
    op.create_index(op.f('ix_customer_sessions_time_consumed'), 'customer_sessions', ['time_consumed'], unique=False)
    op.create_index(op.f('ix_customer_sessions_uploaded_at'), 'customer_sessions', ['uploaded_at'], unique=False)


def downgrade():
    # Drop indexes first
    op.drop_index(op.f('ix_customer_sessions_uploaded_at'), table_name='customer_sessions')
    op.drop_index(op.f('ix_customer_sessions_time_consumed'), table_name='customer_sessions')
    op.drop_index(op.f('ix_customer_sessions_destination'), table_name='customer_sessions')
    op.drop_index(op.f('ix_customer_sessions_source'), table_name='customer_sessions')
    op.drop_index(op.f('ix_customer_sessions_region'), table_name='customer_sessions')
    op.drop_index(op.f('ix_customer_sessions_customer'), table_name='customer_sessions')
    # Drop table
    op.drop_table('customer_sessions')
