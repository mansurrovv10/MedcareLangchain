from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from mysite.api.auth import get_db
from mysite.database.models import Schedule
from mysite.database.schema import ScheduleResponse
from typing import List

router = APIRouter()

@router.get("/", response_model=List[ScheduleResponse])
def get_schedules(db: Session = Depends(get_db)):
    schedules = db.query(Schedule).filter(Schedule.is_booked == False).all()
    return schedules