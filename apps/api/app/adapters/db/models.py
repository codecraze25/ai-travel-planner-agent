from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.adapters.db.base import Base
from app.domain.trip import TripStatus


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(320), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    trips: Mapped[list[TripModel]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class TripModel(Base):
    __tablename__ = "trips"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    origin: Mapped[str] = mapped_column(String(255))
    destination: Mapped[str] = mapped_column(String(255))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    travelers: Mapped[int] = mapped_column(Integer)
    budget_usd: Mapped[float] = mapped_column(Float)
    status: Mapped[TripStatus] = mapped_column(
        Enum(TripStatus, name="trip_status", values_callable=lambda x: [e.value for e in x]),
        default=TripStatus.DRAFT,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped[UserModel] = relationship(back_populates="trips")
    preferences: Mapped[TripPreferencesModel | None] = relationship(
        back_populates="trip", uselist=False, cascade="all, delete-orphan"
    )


class TripPreferencesModel(Base):
    __tablename__ = "trip_preferences"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("trips.id", ondelete="CASCADE"), unique=True, index=True
    )
    style: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)
    hotel_prefs: Mapped[str | None] = mapped_column(Text, nullable=True)
    flight_prefs: Mapped[str | None] = mapped_column(Text, nullable=True)
    food_prefs: Mapped[str | None] = mapped_column(Text, nullable=True)
    activity_prefs: Mapped[str | None] = mapped_column(Text, nullable=True)
    accessibility: Mapped[str | None] = mapped_column(Text, nullable=True)
    visa_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    constraints: Mapped[str | None] = mapped_column(Text, nullable=True)

    trip: Mapped[TripModel] = relationship(back_populates="preferences")
