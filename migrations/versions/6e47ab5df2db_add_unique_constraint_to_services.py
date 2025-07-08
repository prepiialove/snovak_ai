"""Add unique constraint to services

Revision ID: 6e47ab5df2db
Revises: 5a3de769f8f0
Create Date: 2025-07-08 09:06:33.645302

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6e47ab5df2db'
down_revision: Union[str, Sequence[str], None] = '5a3de769f8f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint(
        "uq_service_name_category", "services", ["name", "category_id"]
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("uq_service_name_category", "services", type_="unique")
