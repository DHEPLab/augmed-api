"""create analytics table

Revision ID: cc1f971840fc
Revises: 02d25e5adcad
Create Date: 2025-06-13 16:17:19.503474

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'cc1f971840fc'
down_revision = '02d25e5adcad'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'analytics',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_email', sa.String(128), nullable=False),
        sa.Column('case_config_id', sa.String, nullable=False),
        sa.Column('case_id', sa.Integer, nullable=False),
        sa.Column('case_open_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('answer_open_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('answer_submit_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('to_answer_open_secs', sa.Float, nullable=False),
        sa.Column('to_submit_secs', sa.Float, nullable=False),
        sa.Column('total_duration_secs', sa.Float, nullable=False),
        sa.Column(
            'created_timestamp',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('CURRENT_TIMESTAMP')
        ),
        sa.Column(
            'modified_timestamp',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('CURRENT_TIMESTAMP')
        ),
        sa.UniqueConstraint('user_email', 'case_config_id', name='uq_analytics_user_case')
    )


def downgrade():
    op.drop_table('analytics')
