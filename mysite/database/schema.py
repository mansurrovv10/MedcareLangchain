from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from mysite.database.models import StatusChoices


class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    phone_number: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class SpecialityBase(BaseModel):
    title: str
    description: str

class SpecialityCreate(SpecialityBase):
    pass

class SpecialityResponse(SpecialityBase):
    id: int

    class Config:
        from_attributes = True



class DoctorBase(BaseModel):
    full_name: str
    speciality_id: int
    experience_years: int
    price_per_visit: float

class DoctorCreate(DoctorBase):
    pass

class DoctorResponse(DoctorBase):
    id: int
    speciality: Optional[SpecialityResponse] = None

    class Config:
        from_attributes = True


class ScheduleBase(BaseModel):
    doctor_id: int
    date: str
    start_time: str
    end_time: str
    is_booked: bool = False

class ScheduleCreate(ScheduleBase):
    pass

class ScheduleResponse(ScheduleBase):
    id: int
    doctor: Optional[DoctorResponse] = None

    class Config:
        from_attributes = True


class AppointmentBase(BaseModel):
    user_id: int
    schedule_id: int
    status: StatusChoices = StatusChoices.active

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentResponse(AppointmentBase):
    id: int
    user: Optional[UserResponse] = None
    schedule: Optional[ScheduleResponse] = None

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenRefresh(BaseModel):
    refresh_token: str