"""Add unique constrain to task table

Revision ID: 4b7d79d8a52f
Revises: b3708f6bc9fd
Create Date: 2024-09-10 14:01:32.953585

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4b7d79d8a52f'
down_revision = '822d410d29cb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('task', schema=None) as batch_op:
        batch_op.drop_index('ix_task_user_email')
        batch_op.create_unique_constraint('uq_user_email_case_id', ['user_email', 'case_id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('task', schema=None) as batch_op:
        batch_op.drop_constraint('uq_user_email_case_id', type_='unique')
        batch_op.create_index('ix_task_user_email', ['user_email', 'case_id'], unique=False)

    # ### end Alembic commands ###