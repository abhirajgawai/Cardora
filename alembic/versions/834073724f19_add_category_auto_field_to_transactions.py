"""add category_auto field to transactions

Revision ID: 834073724f19
Revises: b50d9ef2b791
Create Date: 2025-10-29 23:21:12.095858

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '834073724f19'
down_revision: Union[str, None] = 'b50d9ef2b791'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add category_auto column to transactions table
    op.add_column(
        'transactions',
        sa.Column('category_auto', sa.String(length=50), nullable=True),
        schema='cardora'
    )


def downgrade() -> None:
    # Remove category_auto column from transactions table
    op.drop_column('transactions', 'category_auto', schema='cardora')
