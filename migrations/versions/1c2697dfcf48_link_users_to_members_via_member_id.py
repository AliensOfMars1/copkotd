"""link users to members via member_id

Revision ID: 1c2697dfcf48
Revises: d2087935f888
Create Date: 2026-11-12 15:51:12.297073

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1c2697dfcf48'
down_revision = 'd2087935f888'
branch_labels = None
depends_on = None


FK_NAME = "fk_users_member_id_members"
UQ_NAME = "uq_users_member_id"


def upgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('member_id', sa.Integer(), nullable=True))
        batch_op.create_unique_constraint(UQ_NAME, ['member_id'])
        batch_op.create_foreign_key(
            FK_NAME,
            'members',
            ['member_id'],
            ['id'],
            ondelete='SET NULL',
        )


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint(FK_NAME, type_='foreignkey')
        batch_op.drop_constraint(UQ_NAME, type_='unique')
        batch_op.drop_column('member_id')