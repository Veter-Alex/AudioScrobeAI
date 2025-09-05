"""Merge ae8380670e98 and a1f2b3c4d5e6

Revision ID: b3c4d5e6f7g8
Revises: ae8380670e98, a1f2b3c4d5e6
Create Date: 2025-09-05 12:30:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "b3c4d5e6f7g8"
down_revision: Union[str, Sequence[str], None] = ("ae8380670e98", "a1f2b3c4d5e6")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Merge migration: no schema changes, used to join branches."""
    # This is an empty merge migration. All work is performed in child migrations.
    pass


def downgrade() -> None:
    # Nothing to do on downgrade for a merge marker.
    pass
