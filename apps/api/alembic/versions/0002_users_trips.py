"""Add users, trips, and trip_preferences tables.

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-03

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

trip_status = postgresql.ENUM(
    "draft", "planning", "ready", "archived", name="trip_status", create_type=False
)


def upgrade() -> None:
    trip_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("external_id", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_users_external_id", "users", ["external_id"], unique=True)
    op.create_index("ix_users_email", "users", ["email"], unique=False)

    op.create_table(
        "trips",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("origin", sa.String(length=255), nullable=False),
        sa.Column("destination", sa.String(length=255), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("travelers", sa.Integer(), nullable=False),
        sa.Column("budget_usd", sa.Float(), nullable=False),
        sa.Column(
            "status",
            trip_status,
            nullable=False,
            server_default="draft",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_trips_user_id", "trips", ["user_id"], unique=False)

    op.create_table(
        "trip_preferences",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("trip_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("style", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("hotel_prefs", sa.Text(), nullable=True),
        sa.Column("flight_prefs", sa.Text(), nullable=True),
        sa.Column("food_prefs", sa.Text(), nullable=True),
        sa.Column("activity_prefs", sa.Text(), nullable=True),
        sa.Column("accessibility", sa.Text(), nullable=True),
        sa.Column("visa_notes", sa.Text(), nullable=True),
        sa.Column("constraints", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["trip_id"], ["trips.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_trip_preferences_trip_id", "trip_preferences", ["trip_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_trip_preferences_trip_id", table_name="trip_preferences")
    op.drop_table("trip_preferences")
    op.drop_index("ix_trips_user_id", table_name="trips")
    op.drop_table("trips")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_users_external_id", table_name="users")
    op.drop_table("users")
    trip_status.drop(op.get_bind(), checkfirst=True)
