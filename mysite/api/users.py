from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from mysite.database.db import SessionLocal
from mysite.database.models import User
from mysite.database.schema import UserCreate, UserResponse

user_router = APIRouter(prefix="/users", tags=["users"])


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@user_router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    email_exists = db.query(User).filter(User.email == user.email).first()

    if email_exists:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_db = User(
        full_name=user.full_name,
        email=user.email,
        password=user.password,  # Эскертүү: Паролду кааласаңыз хэштеп сактасаңыз болот
        phone_number=user.phone_number
    )

    db.add(user_db)
    db.commit()
    db.refresh(user_db)

    return user_db


@user_router.get("/", response_model=list[UserResponse])
async def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@user_router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user_db = db.query(User).filter(User.id == user_id).first()

    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")

    return user_db


@user_router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user: UserCreate, db: Session = Depends(get_db)):
    user_db = db.query(User).filter(User.id == user_id).first()

    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")

    user_db.full_name = user.full_name
    user_db.email = user.email
    user_db.password = user.password
    user_db.phone_number = user.phone_number

    db.commit()
    db.refresh(user_db)

    return user_db


@user_router.delete("/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    user_db = db.query(User).filter(User.id == user_id).first()

    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user_db)
    db.commit()

    return {"message": "User deleted successfully"}