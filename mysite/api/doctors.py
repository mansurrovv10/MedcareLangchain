from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List


from mysite.api.auth import get_db
from mysite.database.models import Doctor, Speciality
from mysite.database.schema import DoctorResponse, DoctorCreate

router = APIRouter(prefix="/doctors", tags=["Doctors"])


@router.get("/", response_model=List[DoctorResponse])
def get_all_doctors(db: Session = Depends(get_db)):
    """Баардык дарыгерлердин тизмесин кайтарат"""
    doctors = db.query(Doctor).all()
    return doctors


@router.get("/{doctor_id}", response_model=DoctorResponse)
def get_doctor_by_id(doctor_id: int, db: Session = Depends(get_db)):
    """Берилген ID боюнча конкреттүү дарыгерди табат"""
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Дарыгер табылган жок."
        )
    return doctor


@router.post("/", response_model=DoctorResponse, status_code=status.HTTP_201_CREATED)
def create_doctor(doctor_data: DoctorCreate, db: Session = Depends(get_db)):
    """Жаңы дарыгер кошуу (админ үчүн)"""
    # Адистик бар же жок экенин текшерүү
    speciality = db.query(Speciality).filter(Speciality.id == doctor_data.speciality_id).first()
    if not speciality:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Көрсөтүлгөн адистик (Speciality ID) базада табылган жок."
        )

    new_doctor = Doctor(
        full_name=doctor_data.full_name,
        speciality_id=doctor_data.speciality_id,
        experience_years=doctor_data.experience_years,
        price_per_visit=doctor_data.price_per_visit
    )

    db.add(new_doctor)
    db.commit()
    db.refresh(new_doctor)
    return new_doctor