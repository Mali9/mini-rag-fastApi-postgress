"""add project_name column to projects

Revision ID: 958d10ffe8f3
Revises: add_asset_path_column
Create Date: 2025-08-07 23:39:46.431226

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '958d10ffe8f3'
down_revision: Union[str, Sequence[str], None] = 'add_asset_path_column'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('projects', sa.Column('project_name', sa.String(length=255), nullable=True))
    op.add_column('projects', sa.Column('project_description', sa.String(length=255), nullable=True))



def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('projects', 'project_name')
    op.drop_column('projects', 'project_description')
