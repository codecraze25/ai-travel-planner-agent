"""Add flights and hotels tables.

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-03

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "flights",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("trip_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("external_id", sa.String(length=255), nullable=False),
        sa.Column("airline", sa.String(length=255), nullable=False),
        sa.Column("flight_number", sa.String(length=64), nullable=False),
        sa.Column("departure_time", sa.String(length=64), nullable=False),
        sa.Column("arrival_time", sa.String(length=64), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("stops", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("price_usd", sa.Float(), nullable=False),
        sa.Column("baggage_info", sa.Text(), nullable=True),
        sa.Column("booking_link", sa.Text(), nullable=True),
        sa.Column("cancellation_policy", sa.Text(), nullable=True),
        sa.Column("selected", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("raw_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["trip_id"], ["trips.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_flights_trip_id", "flights", ["trip_id"], unique=False)

    op.create_table(
        "hotels",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("trip_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("external_id", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("price_per_night_usd", sa.Float(), nullable=False),
        sa.Column("total_price_usd", sa.Float(), nullable=False),
        sa.Column("rating", sa.Float(), nullable=True),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("amenities", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("cancellation_policy", sa.Text(), nullable=True),
        sa.Column("photo_urls", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("booking_link", sa.Text(), nullable=True),
        sa.Column("selected", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("raw_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["trip_id"], ["trips.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_hotels_trip_id", "hotels", ["trip_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_hotels_trip_id", table_name="hotels")
    op.drop_table("hotels")
    op.drop_index("ix_flights_trip_id", table_name="flights")
    op.drop_table("flights")
