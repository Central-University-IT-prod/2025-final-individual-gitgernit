"""empty message

Revision ID: cd468b0084bd
Revises: 43b3fe35409a
Create Date: 2025-02-22 03:17:50.396186

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'cd468b0084bd'
down_revision: Union[str, None] = '43b3fe35409a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('clicks', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.add_column('impressions', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('impressions', 'created_at')
    op.drop_column('clicks', 'created_at')
    # ### end Alembic commands ###
