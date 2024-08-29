"""add new sub

Revision ID: 909d0853853d
Revises: 9899edee4543
Create Date: 2024-08-25 14:16:20.044157

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "909d0853853d"
down_revision: Union[str, None] = "9899edee4543"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("subscription", sa.Column("price_str", sa.String(), nullable=True))
    op.add_column(
        "subscription", sa.Column("old_price_str", sa.String(), nullable=True)
    )
    op.add_column(
        "subscription", sa.Column("free_period_days", sa.Integer(), nullable=True)
    )
    op.add_column(
        "subscription", sa.Column("free_period_str", sa.String(), nullable=True)
    )
    op.add_column("subscription", sa.Column("comment", sa.String(), nullable=True))
    op.add_column("subscription", sa.Column("discount", sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("subscription", "discount")
    op.drop_column("subscription", "comment")
    op.drop_column("subscription", "free_period_str")
    op.drop_column("subscription", "free_period_days")
    op.drop_column("subscription", "old_price_str")
    op.drop_column("subscription", "price_str")
    # ### end Alembic commands ###
