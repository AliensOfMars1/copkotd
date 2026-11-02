"""add families table and member family_id, drop ministry leader_id

Revision ID: 30c8b74cff1d
Revises: 7a4de08201a1
Create Date: 2026-09-27 14:23:20.968956

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '30c8b74cff1d'
down_revision = '7a4de08201a1'
branch_labels = None
depends_on = None


def upgrade():
    # ── Families table ───────────────────────────────────────
    op.create_table('families',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('leader_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['leader_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # ── members.family_id ────────────────────────────────────
    with op.batch_alter_table('members', schema=None) as batch_op:
        batch_op.add_column(sa.Column('family_id', sa.Integer(), nullable=True))
        batch_op.create_index(batch_op.f('ix_members_family_id'), ['family_id'], unique=False)
        batch_op.create_foreign_key(
            'fk_members_family_id', 'families', ['family_id'], ['id']
        )

    # ── ministries: ensure is_active NOT NULL, drop leader_id ─
    with op.batch_alter_table('ministries', schema=None) as batch_op:
        batch_op.alter_column(
            'is_active',
            existing_type=sa.BOOLEAN(),
            nullable=False,
        )
        # Dropping the column also drops its FK in SQLite batch mode,
        # so no explicit drop_constraint is required.
        batch_op.drop_column('leader_id')


def downgrade():
    with op.batch_alter_table('ministries', schema=None) as batch_op:
        batch_op.add_column(sa.Column('leader_id', sa.INTEGER(), nullable=True))
        batch_op.create_foreign_key(
            'fk_ministries_leader_id', 'users', ['leader_id'], ['id']
        )
        batch_op.alter_column(
            'is_active',
            existing_type=sa.BOOLEAN(),
            nullable=True,
        )

    with op.batch_alter_table('members', schema=None) as batch_op:
        batch_op.drop_constraint('fk_members_family_id', type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_members_family_id'))
        batch_op.drop_column('family_id')

    op.drop_table('families')