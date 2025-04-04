"""Update product image as optional

Revision ID: 723cbf051f86
Revises: f5ed2e53e00b
Create Date: 2025-04-04 12:58:47.195225

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '723cbf051f86'
down_revision: Union[str, None] = 'f5ed2e53e00b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('product', 'cover_image_key',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('product', 'cover_image_key',
               existing_type=sa.VARCHAR(),
               nullable=False)
    # ### end Alembic commands ###
