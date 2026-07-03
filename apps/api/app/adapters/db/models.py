from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.adapters.db.base import Base
from app.domain.documents import DocumentStatus
from app.domain.email import EmailStatus, EmailTemplate
from app.domain.trip import TripStatus


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    external_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(320), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    trips: Mapped[list[TripModel]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    traveler_profile: Mapped[TravelerProfileModel | None] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )


class TravelerProfileModel(Base):
    __tablename__ = "traveler_profiles"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True
    )
    full_name: Mapped[str] = mapped_column(String(200))
    nationality: Mapped[str | None] = mapped_column(String(100), nullable=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    passport_number_enc: Mapped[str | None] = mapped_column(Text, nullable=True)
    passport_expiry: Mapped[date | None] = mapped_column(Date, nullable=True)
    preferences_json: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped[UserModel] = relationship(back_populates="traveler_profile")


class TripModel(Base):
    __tablename__ = "trips"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    origin: Mapped[str] = mapped_column(String(255))
    destination: Mapped[str] = mapped_column(String(255))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    travelers: Mapped[int] = mapped_column(Integer)
    budget_usd: Mapped[float] = mapped_column(Float)
    status: Mapped[TripStatus] = mapped_column(
        Enum(
            TripStatus,
            name="trip_status",
            values_callable=lambda x: [e.value for e in x],
            native_enum=False,
        ),
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
    flights: Mapped[list[FlightModel]] = relationship(
        back_populates="trip", cascade="all, delete-orphan"
    )
    hotels: Mapped[list[HotelModel]] = relationship(
        back_populates="trip", cascade="all, delete-orphan"
    )
    documents: Mapped[list[DocumentModel]] = relationship(
        back_populates="trip", cascade="all, delete-orphan"
    )
    itineraries: Mapped[list[ItineraryModel]] = relationship(
        back_populates="trip", cascade="all, delete-orphan"
    )
    agent_actions: Mapped[list[AgentActionModel]] = relationship(
        back_populates="trip", cascade="all, delete-orphan"
    )
    emails: Mapped[list[EmailModel]] = relationship(
        back_populates="trip", cascade="all, delete-orphan"
    )
    audit_logs: Mapped[list[AuditLogModel]] = relationship(
        back_populates="trip", cascade="all, delete-orphan"
    )


class TripPreferencesModel(Base):
    __tablename__ = "trip_preferences"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    trip_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("trips.id", ondelete="CASCADE"), unique=True, index=True
    )
    style: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    hotel_prefs: Mapped[str | None] = mapped_column(Text, nullable=True)
    flight_prefs: Mapped[str | None] = mapped_column(Text, nullable=True)
    food_prefs: Mapped[str | None] = mapped_column(Text, nullable=True)
    activity_prefs: Mapped[str | None] = mapped_column(Text, nullable=True)
    accessibility: Mapped[str | None] = mapped_column(Text, nullable=True)
    visa_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    constraints: Mapped[str | None] = mapped_column(Text, nullable=True)

    trip: Mapped[TripModel] = relationship(back_populates="preferences")


class FlightModel(Base):
    __tablename__ = "flights"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    trip_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("trips.id", ondelete="CASCADE"), index=True
    )
    external_id: Mapped[str] = mapped_column(String(255))
    airline: Mapped[str] = mapped_column(String(255))
    flight_number: Mapped[str] = mapped_column(String(64))
    departure_time: Mapped[str] = mapped_column(String(64))
    arrival_time: Mapped[str] = mapped_column(String(64))
    duration_minutes: Mapped[int] = mapped_column(Integer)
    stops: Mapped[int] = mapped_column(Integer, default=0)
    price_usd: Mapped[float] = mapped_column(Float)
    baggage_info: Mapped[str | None] = mapped_column(Text, nullable=True)
    booking_link: Mapped[str | None] = mapped_column(Text, nullable=True)
    cancellation_policy: Mapped[str | None] = mapped_column(Text, nullable=True)
    selected: Mapped[bool] = mapped_column(Boolean, default=False)
    raw_json: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    trip: Mapped[TripModel] = relationship(back_populates="flights")


class HotelModel(Base):
    __tablename__ = "hotels"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    trip_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("trips.id", ondelete="CASCADE"), index=True
    )
    external_id: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(255))
    price_per_night_usd: Mapped[float] = mapped_column(Float)
    total_price_usd: Mapped[float] = mapped_column(Float)
    rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    amenities: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    cancellation_policy: Mapped[str | None] = mapped_column(Text, nullable=True)
    photo_urls: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    booking_link: Mapped[str | None] = mapped_column(Text, nullable=True)
    selected: Mapped[bool] = mapped_column(Boolean, default=False)
    raw_json: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    trip: Mapped[TripModel] = relationship(back_populates="hotels")


class DocumentModel(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    trip_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("trips.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    filename: Mapped[str] = mapped_column(String(512))
    s3_key: Mapped[str] = mapped_column(String(1024))
    mime_type: Mapped[str] = mapped_column(String(128), default="application/pdf")
    size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[DocumentStatus] = mapped_column(
        Enum(
            DocumentStatus,
            name="document_status",
            values_callable=lambda x: [e.value for e in x],
            native_enum=False,
        ),
        default=DocumentStatus.UPLOADED,
    )
    extracted_fields: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    injection_flagged: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    trip: Mapped[TripModel] = relationship(back_populates="documents")
    chunks: Mapped[list[DocumentChunkModel]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )


class DocumentChunkModel(Base):
    __tablename__ = "document_chunks"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("documents.id", ondelete="CASCADE"), index=True
    )
    chunk_index: Mapped[int] = mapped_column(Integer)
    content: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float] | None] = mapped_column(JSON, nullable=True)

    document: Mapped[DocumentModel] = relationship(back_populates="chunks")


class ItineraryModel(Base):
    __tablename__ = "itineraries"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    trip_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("trips.id", ondelete="CASCADE"), index=True
    )
    version: Mapped[int] = mapped_column(Integer, default=1)
    total_est_cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    trip: Mapped[TripModel] = relationship(back_populates="itineraries")
    items: Mapped[list[ItineraryItemModel]] = relationship(
        back_populates="itinerary", cascade="all, delete-orphan"
    )


class ItineraryItemModel(Base):
    __tablename__ = "itinerary_items"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    itinerary_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("itineraries.id", ondelete="CASCADE"), index=True
    )
    day_number: Mapped[int] = mapped_column(Integer)
    time_block: Mapped[str] = mapped_column(String(32))
    title: Mapped[str] = mapped_column(String(512))
    description: Mapped[str] = mapped_column(Text)
    location: Mapped[str | None] = mapped_column(String(512), nullable=True)
    est_cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
    map_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    backup_option: Mapped[str | None] = mapped_column(Text, nullable=True)

    itinerary: Mapped[ItineraryModel] = relationship(back_populates="items")


class AgentActionModel(Base):
    __tablename__ = "agent_actions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    trip_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("trips.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    tool_name: Mapped[str] = mapped_column(String(128))
    input_json: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    output_json: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    success: Mapped[bool] = mapped_column(Boolean, default=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    correlation_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    trip: Mapped[TripModel] = relationship(back_populates="agent_actions")


class EmailModel(Base):
    __tablename__ = "emails"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    trip_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("trips.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    template: Mapped[EmailTemplate] = mapped_column(
        Enum(
            EmailTemplate,
            name="email_template",
            values_callable=lambda x: [e.value for e in x],
            native_enum=False,
        ),
        default=EmailTemplate.ITINERARY_SUMMARY,
    )
    status: Mapped[EmailStatus] = mapped_column(
        Enum(
            EmailStatus,
            name="email_status",
            values_callable=lambda x: [e.value for e in x],
            native_enum=False,
        ),
        default=EmailStatus.DRAFT,
    )
    recipients: Mapped[str] = mapped_column(String(1024))
    subject: Mapped[str] = mapped_column(String(512))
    body_text: Mapped[str] = mapped_column(Text)
    body_html: Mapped[str] = mapped_column(Text)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    provider_message_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    trip: Mapped[TripModel] = relationship(back_populates="emails")


class AuditLogModel(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    trip_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("trips.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    action: Mapped[str] = mapped_column(String(128))
    details: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    trip: Mapped[TripModel] = relationship(back_populates="audit_logs")
