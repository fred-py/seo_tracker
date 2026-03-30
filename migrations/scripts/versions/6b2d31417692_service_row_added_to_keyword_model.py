"""service row added to keyword model

Revision ID: 6b2d31417692
Revises: d57d25d7987b
Create Date: 2025-10-18 18:51:44.889460

# https://testdriven.io/blog/fastapi-sqlmodel/#async-sqlmodel

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '6b2d31417692'
down_revision: Union[str, Sequence[str], None] = 'd57d25d7987b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
