import datetime

from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
    Boolean,
    DateTime,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, DeclarativeBase, mapped_column, Mapped


class Base(DeclarativeBase):
    pass


class Experiment(Base):
    __tablename__ = "experiments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    key: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str]
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now(datetime.UTC)
    )

    variants: Mapped[list["Variant"]] = relationship(back_populates="experiment")


class Variant(Base):
    __tablename__ = "variants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    experiment_id: Mapped[int] = mapped_column(ForeignKey("experiments.id"))
    key: Mapped[str]
    payload: Mapped[str]
    weight: Mapped[float]

    experiment: Mapped[Experiment] = relationship(back_populates="variants")


class DeviceAssignment(Base):
    __tablename__ = "assignments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    device_id: Mapped[str] = mapped_column(String, index=True)
    experiment_id: Mapped[int]
    variant_id: Mapped[int]
    assigned_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now(datetime.UTC)
    )

    __table_args__ = (
        UniqueConstraint("device_id", "experiment_id", name="uq_assignment"),
    )


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    device_id: Mapped[str] = mapped_column(String, index=True, unique=True)
