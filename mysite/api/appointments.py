from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from mysite.api.auth import get_db
from mysite.database.models import Appointment, Schedule
from mysite.database.schema import AppointmentCreate, AppointmentResponse

router = APIRouter()


@router.post("/", response_model=AppointmentResponse)
def create_appointment(data: AppointmentCreate, db: Session = Depends(get_db)):
    schedule = db.query(Schedule).filter(Schedule.id == data.schedule_id).first()

    if not schedule:
        raise HTTPException(status_code=404, detail="График табылган жок.")

    if schedule.is_booked:
        raise HTTPException(status_code=400, detail="Бул убакыт эбак бронь кылынган.")


    schedule.is_booked = True

    new_appointment = Appointment(
        user_id=data.user_id,
        schedule_id=data.schedule_id,
        status=data.status
    )

    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    return new_appointment