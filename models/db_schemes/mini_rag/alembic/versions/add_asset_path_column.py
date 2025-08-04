"""Add asset_path column

Revision ID: add_asset_path_column
Revises: 32493323dc69
Create Date: 2025-08-02 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_asset_path_column'
down_revision: Union[str, Sequence[str], None] = '32493323dc69'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add asset_path column
    op.add_column('assets', sa.Column('asset_path', sa.String(), nullable=True))
    
    # Remove asset_config column
    op.drop_column('assets', 'asset_config')
    
    # Make asset_path not nullable after data migration
    op.alter_column('assets', 'asset_path', nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Add asset_config column back
    op.add_column('assets', sa.Column('asset_config', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    
    # Remove asset_path column
    op.drop_column('assets', 'asset_path')
    
    # Make asset_config not nullable
    op.alter_column('assets', 'asset_config', nullable=False) 