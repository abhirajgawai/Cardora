"""add unique category name per user and system

Revision ID: a3c1f9d2e4b7
Revises: 8fd5771a4044
Create Date: 2026-08-31

A user cannot create two custom categories with the same name, and a custom
category may not shadow a system category name (enforced in the router too —
this index is the DB-level guard). System categories themselves are excluded
(user_id IS NULL) because seeding may legitimately reuse names across nothing.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a3c1f9d2e4b7'
down_revision = '8fd5771a4044'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        'ux_cardora_categories_user_name',
        'categories',
        ['user_id', 'name'],
        unique=True,
        schema='cardora',
        postgresql_where=sa.text('user_id IS NOT NULL'),
    )


def downgrade() -> None:
    op.drop_index('ux_cardora_categories_user_name', table_name='categories', schema='cardora')
