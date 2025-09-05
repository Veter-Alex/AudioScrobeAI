"""Drop operations column from ai_models

Revision ID: d4e5f6g7h8i9
Revises: b3c4d5e6f7g8
Create Date: 2025-09-05 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d4e5f6g7h8i9"
down_revision: Union[str, Sequence[str], None] = "b3c4d5e6f7g8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Remove the legacy 'operations' column if present."""
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if 'ai_models' in inspector.get_table_names():
        cols = [c['name'] for c in inspector.get_columns('ai_models')]
        if 'operations' in cols:
            # use IF EXISTS to be safe if concurrent state differs
            op.execute('ALTER TABLE ai_models DROP COLUMN IF EXISTS operations;')


def downgrade() -> None:
    """Restore the 'operations' column as an ARRAY of the existing enum type.

    This best-effort downgrade recreates the column (nullable) so downgrade won't fail,
    but it doesn't repopulate previous values.
    """
    operation_enum = sa.Enum('transcription', 'translation', 'summary', name='operation')
    try:
        op.add_column('ai_models', sa.Column('operations', sa.ARRAY(operation_enum), nullable=True))
    except Exception:
        # best-effort: if add fails (e.g., table missing) ignore
        pass
