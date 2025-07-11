"""Add ai_score_shown boolean to Answer

Revision ID: 5ec038ebcfe5
Revises: cc1f971840fc
Create Date: 2025-06-19 20:16:37.775435

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '5ec038ebcfe5'
down_revision = 'cc1f971840fc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # op.drop_table('features')
    # op.drop_table('synth_recruits')
    # op.drop_table('case_assignment')
    # op.drop_table('cases')
    # op.drop_table('participants')
    with op.batch_alter_table('analytics', schema=None) as batch_op:
        batch_op.alter_column('created_timestamp',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('modified_timestamp',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))

    with op.batch_alter_table('answer', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                'ai_score_shown',
                sa.Boolean(),
                nullable=False,
                server_default=sa.text('false')  # <<< fill existing rows with FALSE
            )
        )
        batch_op.alter_column('task_id',
               existing_type=sa.VARCHAR(),
               nullable=True)
        batch_op.alter_column('user_email',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.String(length=128),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('answer', schema=None) as batch_op:
        batch_op.alter_column('user_email',
               existing_type=sa.String(length=128),
               type_=sa.VARCHAR(length=255),
               existing_nullable=True)
        batch_op.alter_column('task_id',
               existing_type=sa.VARCHAR(),
               nullable=False)
        batch_op.drop_column('ai_score_shown')

    with op.batch_alter_table('analytics', schema=None) as batch_op:
        batch_op.alter_column('modified_timestamp',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('created_timestamp',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))

    op.create_table('participants',
    sa.Column('participant_id', sa.INTEGER(), server_default=sa.text("nextval('participants_participant_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('person_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['person_id'], ['synth_recruits.person_id'], name='participants_person_id_fkey'),
    sa.PrimaryKeyConstraint('participant_id', name='participants_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_table('cases',
    sa.Column('case_id', sa.INTEGER(), server_default=sa.text("nextval('cases_case_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('title', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('vignette', sa.TEXT(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('case_id', name='cases_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_table('case_assignment',
    sa.Column('participant_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('case_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('show_ai', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('features_shown', postgresql.JSONB(astext_type=sa.Text()), autoincrement=False, nullable=False),
    sa.Column('assigned_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['case_id'], ['cases.case_id'], name='case_assignment_case_id_fkey'),
    sa.ForeignKeyConstraint(['participant_id'], ['participants.participant_id'], name='case_assignment_participant_id_fkey'),
    sa.PrimaryKeyConstraint('participant_id', 'case_id', name='case_assignment_pkey')
    )
    op.create_table('synth_recruits',
    sa.Column('person_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('age_group', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('gender', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('mh_ibs', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('mh_ast', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('mh_anx_dep', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('fh_diab', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('fh_cancer', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('fh_hypert', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('fh_crc', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('bmi', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('mh_mig', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('mh_oa', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('mh_hypo', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('apd', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('const', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('cd', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('rb', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('mh_hypert2', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('mh_hyperl', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('mh_diab2', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('ta', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('bss', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('ha', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('fat', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('sob', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('crc_risk_low', sa.NUMERIC(), autoincrement=False, nullable=True),
    sa.Column('crc_risk_medium', sa.NUMERIC(), autoincrement=False, nullable=True),
    sa.Column('crc_risk_high', sa.NUMERIC(), autoincrement=False, nullable=True),
    sa.Column('crc_score', sa.NUMERIC(), autoincrement=False, nullable=True),
    sa.Column('crc_risk_adjusted', sa.NUMERIC(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('person_id', name='synth_recruits_pkey')
    )
    op.create_table('features',
    sa.Column('feature_name', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('feature_name', name='features_pkey')
    )
    # ### end Alembic commands ###
