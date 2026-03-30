"""populate checked_date from keyword created_date

Revision ID: d57d25d7987b
Revises: b21660f3e3ad
Create Date: 2025-10-18 18:09:20.334846

# https://testdriven.io/blog/fastapi-sqlmodel/#async-sqlmodel

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'd57d25d7987b'
down_revision: Union[str, Sequence[str], None] = 'b21660f3e3ad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Copy created_date from keyword to organicrank.checked_date
    op.execute("""
        UPDATE organicrank 
        SET checked_date = keyword.created_date 
        FROM keyword 
        WHERE organicrank.keyword_id = keyword.id
    """)


def downgrade() -> None:
    # Set checked_date back to null
    op.execute("UPDATE organicrank SET checked_date = NULL")
