"""Location.location unique param has been reverted to True

Revision ID: 344b41b946ad
Revises: 6b2d31417692
Create Date: 2025-10-18 19:23:27.605224

# https://testdriven.io/blog/fastapi-sqlmodel/#async-sqlmodel

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '344b41b946ad'
down_revision: Union[str, Sequence[str], None] = '6b2d31417692'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
