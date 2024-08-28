"""first migration

Revision ID: b2e9ddb43314
Revises: 
Create Date: 2024-08-14 15:06:45.996676

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b2e9ddb43314"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "achievement",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("pictureLink", sa.String(), nullable=True),
        sa.Column("category", sa.String(), nullable=True),
        sa.Column("stage", sa.Integer(), nullable=True),
        sa.Column("target", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_achievement_id"), "achievement", ["id"], unique=False)
    op.create_table(
        "error",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("message", sa.String(), nullable=True),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("is_send", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_error_id"), "error", ["id"], unique=False)
    op.create_table(
        "feedback",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("stars", sa.Integer(), nullable=False),
        sa.Column("message", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_feedback_id"), "feedback", ["id"], unique=False)
    op.create_table(
        "subscription",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("price", sa.Integer(), nullable=True),
        sa.Column("old_price", sa.Integer(), nullable=True),
        sa.Column("months", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_subscription_id"), "subscription", ["id"], unique=False)
    op.create_table(
        "topic",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("title"),
    )
    op.create_index(op.f("ix_topic_id"), "topic", ["id"], unique=False)
    op.create_table(
        "bill",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("label", sa.String(), nullable=True),
        sa.Column("sub_type", sa.Integer(), nullable=True),
        sa.Column("amount", sa.Integer(), nullable=True),
        sa.Column("success", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(
            ["sub_type"],
            ["subscription.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_bill_id"), "bill", ["id"], unique=False)
    op.create_table(
        "subtopic",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("pictureLink", sa.String(), nullable=True),
        sa.Column("topic_title", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["topic_title"],
            ["topic.title"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("title"),
    )
    op.create_index(op.f("ix_subtopic_id"), "subtopic", ["id"], unique=False)
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(), nullable=False),
        sa.Column("username", sa.String(), nullable=True),
        sa.Column("firstname", sa.String(), nullable=True),
        sa.Column("lastname", sa.String(), nullable=True),
        sa.Column("avatar_url", sa.String(), nullable=True),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("vk_id", sa.String(), nullable=True),
        sa.Column("google_id", sa.String(), nullable=True),
        sa.Column("phone_number", sa.String(), nullable=True),
        sa.Column("birth_date", sa.DateTime(), nullable=True),
        sa.Column("hashed_password", sa.String(), nullable=True),
        sa.Column("latest_study", sa.DateTime(), nullable=True),
        sa.Column("latest_update", sa.DateTime(), nullable=True),
        sa.Column("subscription_acquisition", sa.DateTime(), nullable=True),
        sa.Column("subscription_type", sa.Integer(), nullable=True),
        sa.Column("days", sa.Integer(), nullable=True),
        sa.Column("allowed_audio_seconds", sa.Integer(), nullable=True),
        sa.Column("allowed_video_seconds", sa.Integer(), nullable=True),
        sa.Column("energy", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_superuser", sa.Boolean(), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["subscription_type"],
            ["subscription.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_id"), "user", ["id"], unique=False)
    op.create_table(
        "user_achievement",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("achievement_id", sa.Integer(), nullable=True),
        sa.Column("progress", sa.Integer(), nullable=True),
        sa.Column("progress_percent", sa.Float(), nullable=True),
        sa.Column("is_completed", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(
            ["achievement_id"],
            ["achievement.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_user_achievement_id"), "user_achievement", ["id"], unique=False
    )
    op.create_table(
        "word",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("enValue", sa.String(), nullable=True),
        sa.Column("ruValue", sa.String(), nullable=True),
        sa.Column("audioLink", sa.String(), nullable=True),
        sa.Column("pictureLink", sa.String(), nullable=True),
        sa.Column("topic", sa.String(), nullable=True),
        sa.Column("subtopic", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["subtopic"],
            ["subtopic.title"],
        ),
        sa.ForeignKeyConstraint(
            ["topic"],
            ["topic.title"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_word_id"), "word", ["id"], unique=False)
    op.create_table(
        "user_word",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("word_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("frequency", sa.Integer(), nullable=True),
        sa.Column("progress", sa.Integer(), nullable=True),
        sa.Column("latest_study", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["word_id"],
            ["word.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_word_id"), "user_word", ["id"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_user_word_id"), table_name="user_word")
    op.drop_table("user_word")
    op.drop_index(op.f("ix_word_id"), table_name="word")
    op.drop_table("word")
    op.drop_index(op.f("ix_user_achievement_id"), table_name="user_achievement")
    op.drop_table("user_achievement")
    op.drop_index(op.f("ix_user_id"), table_name="user")
    op.drop_table("user")
    op.drop_index(op.f("ix_subtopic_id"), table_name="subtopic")
    op.drop_table("subtopic")
    op.drop_index(op.f("ix_bill_id"), table_name="bill")
    op.drop_table("bill")
    op.drop_index(op.f("ix_topic_id"), table_name="topic")
    op.drop_table("topic")
    op.drop_index(op.f("ix_subscription_id"), table_name="subscription")
    op.drop_table("subscription")
    op.drop_index(op.f("ix_feedback_id"), table_name="feedback")
    op.drop_table("feedback")
    op.drop_index(op.f("ix_error_id"), table_name="error")
    op.drop_table("error")
    op.drop_index(op.f("ix_achievement_id"), table_name="achievement")
    op.drop_table("achievement")
    # ### end Alembic commands ###
