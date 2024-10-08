"""add uwords uid and onboarding

Revision ID: 9899edee4543
Revises: 7a720366b2b7
Create Date: 2024-08-24 17:32:02.747590

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9899edee4543"
down_revision: Union[str, None] = "7a720366b2b7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("user", sa.Column("uwords_uid", sa.String(), nullable=True))
    op.add_column(
        "user", sa.Column("is_onboarding_complete", sa.Boolean(), nullable=True)
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("user", "is_onboarding_complete")
    op.drop_column("user", "uwords_uid")
    # ### end Alembic commands ###
