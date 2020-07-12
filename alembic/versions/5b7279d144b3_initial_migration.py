"""initial migration

Revision ID: 5b7279d144b3
Revises: 
Create Date: 2020-07-07 23:52:35.225334

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '5b7279d144b3'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'error_trace',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('device_number', sa.String(), nullable=False),
        sa.Column('error_code', sa.String(), nullable=False),
        sa.Column('event_code', sa.String(), nullable=False),
        sa.Column('message_date', sa.DateTime()))

    op.create_table(
        'error_type',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('error_code', sa.Integer(), nullable=False),
        sa.Column('description', sa.String()),
        sa.Column('limit', sa.Integer(), nullable=False),
        sa.Column('critical', sa.SmallInteger(), nullable=False))

    op.create_table(
        'event_format',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('event_code', sa.Integer(), nullable=False),
        sa.Column('event_description', sa.String()))

    op.create_table(
        'service',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('port', sa.Integer(), nullable=False, unique=True),
        sa.Column('ip_address', sa.String(), nullable=False))

    op.create_index(op.f('ix_error_trace_device_number'), 'error_trace', ['device_number'], unique=False)
    op.create_index(op.f('ix_error_trace_error_code'), 'error_trace', ['error_code'], unique=False)
    op.create_index(op.f('ix_error_type_error_code'), 'error_type', ['error_code'], unique=False)
    op.create_index(op.f('ix_event_format_event_code'), 'event_format', ['event_code'], unique=False)
    op.create_index(op.f('ix_service_port'), 'service', ['port'], unique=False)


def downgrade():
    op.drop_table('error_trace')
    op.drop_table('error_type')
    op.drop_table('event_format')
    op.drop_table('service')

    op.drop_index("ix_error_trace_device_number", table_name='error_trace')
    op.drop_index("ix_error_trace_error_code", table_name='error_trace')
    op.drop_index("ix_error_type_error_code", table_name='error_type')
    op.drop_index("ix_event_format_event_code", table_name='event_format')
    op.drop_index("ix_service_port", table_name='service')
