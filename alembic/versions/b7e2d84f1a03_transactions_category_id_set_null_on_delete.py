"""transactions.category_id ON DELETE SET NULL

Revision ID: b7e2d84f1a03
Revises: a3c1f9d2e4b7
Create Date: 2026-08-31

DELETE /categories/{id} now exists. transactions.category_id -> categories.id
had no ON DELETE rule (defaults to NO ACTION), so deleting a custom category
with any transactions attached raised an unhandled IntegrityError (500)
instead of the documented "transactions become uncategorized" behavior.
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'b7e2d84f1a03'
down_revision = 'a3c1f9d2e4b7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint(
        'transactions_category_id_fkey',
        'transactions',
        schema='cardora',
        type_='foreignkey',
    )
    op.create_foreign_key(
        'transactions_category_id_fkey',
        'transactions',
        'categories',
        ['category_id'],
        ['id'],
        source_schema='cardora',
        referent_schema='cardora',
        ondelete='SET NULL',
    )


def downgrade() -> None:
    op.drop_constraint(
        'transactions_category_id_fkey',
        'transactions',
        schema='cardora',
        type_='foreignkey',
    )
    op.create_foreign_key(
        'transactions_category_id_fkey',
        'transactions',
        'categories',
        ['category_id'],
        ['id'],
        source_schema='cardora',
        referent_schema='cardora',
    )
