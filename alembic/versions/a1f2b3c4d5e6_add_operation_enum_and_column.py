"""
Add operation enum type and operation column to ai_models

Revision ID: a1f2b3c4d5e6
Revises: e23b3e6ae444
Create Date: 2025-09-05 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a1f2b3c4d5e6"
down_revision: Union[str, Sequence[str], None] = "e23b3e6ae444"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: create enum type and add operation column."""

    # Create new enum type 'operation' if it doesn't exist
    op.execute(
        "DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'operation') THEN CREATE TYPE operation AS ENUM ('transcription','translation','summary'); END IF; END $$;"
    )

    # Add nullable operation column using the new enum type if table exists
    operation_enum = sa.Enum('transcription', 'translation', 'summary', name='operation')
    # Only add the column if the table exists and column is not present
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if 'ai_models' in inspector.get_table_names():
        columns = [c['name'] for c in inspector.get_columns('ai_models')]
        if 'operation' not in columns:
            op.add_column(
                'ai_models',
                sa.Column('operation', operation_enum, nullable=True),
            )

            # If database already had data and an 'operations' ARRAY column, migration
            # would need to copy values; for an empty DB this step is not necessary.

            # Make the column non-nullable to match the model contract
            op.alter_column('ai_models', 'operation', nullable=False)


def downgrade() -> None:
    """Downgrade schema: restore previous state by removing operation column and type."""

    # Add back an 'operations' column as ARRAY of enum (best-effort)
    try:
        operations_enum = sa.Enum('transcription', 'translation', 'summary', name='operation')
        op.add_column('ai_models', sa.Column('operations', sa.ARRAY(operations_enum), nullable=True))
    except Exception:
        # If adding fails, continue with best-effort downgrade
        pass

    # Drop the operation column
    op.drop_column('ai_models', 'operation')

    # Drop enum type
    op.execute('DROP TYPE IF EXISTS operation')
