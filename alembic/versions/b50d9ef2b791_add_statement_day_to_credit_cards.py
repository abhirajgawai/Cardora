"""Add statement_day to credit_cards

Revision ID: b50d9ef2b791
Revises: 166a1bcd7234
Create Date: 2025-10-29 15:18:40.642053

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b50d9ef2b791'
down_revision: Union[str, None] = '166a1bcd7234'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add statement_day column to credit_cards table
    op.add_column(
        'credit_cards',
        sa.Column('statement_day', sa.String(length=50), nullable=True),
        schema='cardora'
    )


def downgrade() -> None:
    # Remove statement_day column from credit_cards table
    op.drop_column('credit_cards', 'statement_day', schema='cardora')
