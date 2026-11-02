"""add member photos, birthdays, homepage content, and site settings

Revision ID: b8f7a2c4e1d9
Revises: 30c8b74cff1d
Create Date: 2026-11-02 20:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b8f7a2c4e1d9'
down_revision = '30c8b74cff1d'
branch_labels = None
depends_on = None


def upgrade():
    # ── homepage_content table ───────────────────────────────
    op.create_table(
        'homepage_content',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('content_type', sa.String(length=40), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=True),
        sa.Column('body', sa.Text(), nullable=True),
        sa.Column('event_date', sa.Date(), nullable=True),
        sa.Column('event_time', sa.String(length=40), nullable=True),
        sa.Column('location', sa.String(length=200), nullable=True),
        sa.Column('image_url', sa.String(length=500), nullable=True),
        sa.Column('speaker', sa.String(length=120), nullable=True),
        sa.Column('video_url', sa.String(length=500), nullable=True),
        sa.Column('service_name', sa.String(length=80), nullable=True),
        sa.Column('day_of_week', sa.String(length=20), nullable=True),
        sa.Column('start_time', sa.String(length=20), nullable=True),
        sa.Column('end_time', sa.String(length=20), nullable=True),
        sa.Column('is_published', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('publish_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('homepage_content', schema=None) as batch_op:
        batch_op.create_index('ix_homepage_content_content_type', ['content_type'], unique=False)

    # ── site_settings table ──────────────────────────────────
    op.create_table(
        'site_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(length=80), nullable=False),
        sa.Column('value', sa.Text(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('site_settings', schema=None) as batch_op:
        batch_op.create_index('ix_site_settings_key', ['key'], unique=True)

    # ── members.photo_url ────────────────────────────────────
    with op.batch_alter_table('members', schema=None) as batch_op:
        batch_op.add_column(sa.Column('photo_url', sa.String(length=500), nullable=True))

    # ── members.birthday_public ──────────────────────────────
    with op.batch_alter_table('members', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('birthday_public', sa.Boolean(), nullable=False, server_default='1')
        )


def downgrade():
    with op.batch_alter_table('members', schema=None) as batch_op:
        batch_op.drop_column('birthday_public')
        batch_op.drop_column('photo_url')

    op.drop_table('site_settings')

    with op.batch_alter_table('homepage_content', schema=None) as batch_op:
        batch_op.drop_index('ix_homepage_content_content_type')
    op.drop_table('homepage_content')