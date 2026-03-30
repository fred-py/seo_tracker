"""Location.location unique param has been reverted to True - service added to Keyword model

Revision ID: 8e53cfd9c2a7
Revises: 344b41b946ad
Create Date: 2025-10-18 19:28:55.741131

# https://testdriven.io/blog/fastapi-sqlmodel/#async-sqlmodel

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '8e53cfd9c2a7'
down_revision: Union[str, Sequence[str], None] = '344b41b946ad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
