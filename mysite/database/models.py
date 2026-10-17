from .db import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Enum, Date, ForeignKey, Text, Boolean, DateTime, Float
from typing import Optional, List
from datetime import date, datetime
from enum import Enum as PyEnum

class StatusChoices(str, PyEnum):
    active = "confirmed"
    inactive = "cancelled"


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String, unique=True)
    password: Mapped[str] = mapped_column(String)
    phone_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    appointments: Mapped[List["Appointment"]] = relationship("Appointment", back_populates="user",
                                                             cascade="all, delete-orphan")
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship("RefreshToken", back_populates="user",
                                                                 cascade="all, delete-orphan")


class RefreshToken(Base):
    __tablename__ = 'refresh_token'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    token: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship('User', back_populates='refresh_tokens')


class Speciality(Base):
    __tablename__ = 'specialities'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, unique=True)
    description: Mapped[str] = mapped_column(String)

    doctors: Mapped[List["Doctor"]] = relationship("Doctor", back_populates="speciality",
                                                   cascade="all, delete-orphan")


class Doctor(Base):
    __tablename__ = 'doctors'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String)
    speciality_id: Mapped[int] = mapped_column(ForeignKey('specialities.id'))
    experience_years: Mapped[int] = mapped_column(Integer, default=0)
    price_per_visit: Mapped[float] = mapped_column(Float)

    speciality: Mapped[Speciality] = relationship(Speciality, back_populates="doctors")
    schedules: Mapped[List["Schedule"]] = relationship("Schedule", back_populates="doctor",
                                                       cascade="all, delete-orphan")


class Schedule(Base):
    __tablename__ = 'schedules'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey('doctors.id'))
    date: Mapped[str] = mapped_column(String)
    start_time: Mapped[str] = mapped_column(String)
    end_time: Mapped[str] = mapped_column(String)
    is_booked: Mapped[bool] = mapped_column(Boolean, default=False)

    doctor: Mapped[Doctor] = relationship(Doctor, back_populates="schedules")
    appointment: Mapped[Optional["Appointment"]] = relationship("Appointment", back_populates="schedule",
                                                                uselist=False, cascade="all, delete-orphan")


class Appointment(Base):
    __tablename__ = 'appointments'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    schedule_id: Mapped[int] = mapped_column(ForeignKey('schedules.id'), unique=True)
    status: Mapped[StatusChoices] = mapped_column(Enum(StatusChoices), default=StatusChoices.active)

    user: Mapped[User] = relationship(User, back_populates="appointments")
    schedule: Mapped[Schedule] = relationship(Schedule, back_populates="appointment")