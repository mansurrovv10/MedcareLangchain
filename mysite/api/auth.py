from datetime import timedelta, datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, Body
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from mysite.database.models import User, RefreshToken
from mysite.database.db import SessionLocal
from mysite.database.schema import UserCreate, UserLogin, UserResponse, TokenResponse
from config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

auth_router = APIRouter(prefix="/auth", tags=["auth"])


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


credentials_exception = HTTPException(
    status_code=401,
    detail="Could not validate credentials.",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        subject = payload.get("sub")

        if subject is None:
            raise credentials_exception

        user_id = int(subject)

    except (JWTError, ValueError, TypeError):
        raise credentials_exception

    user_db = db.query(User).filter(User.id == user_id).first()

    if not user_db:
        raise credentials_exception

    return user_db


def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta if expires_delta
        else timedelta(minutes=settings.ACCESS_TOKEN_LIFETIME)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


def create_refresh_token(data: dict):
    return create_access_token(
        data,
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_LIFETIME)
    )


def get_token_data(user: User):
    return {
        "sub": str(user.id)
    }


@auth_router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    email_exists = db.query(User).filter(User.email == user.email).first()

    if email_exists:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_data = User(
        full_name=user.full_name,
        email=user.email,
        password=get_password_hash(user.password),
        phone_number=user.phone_number
    )

    db.add(user_data)
    db.commit()
    db.refresh(user_data)

    return user_data


@auth_router.post("/login", response_model=TokenResponse)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    user_db = db.query(User).filter(User.email == user.email).first()

    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(user.password, user_db.password):
        raise HTTPException(status_code=401, detail="Invalid password")

    token_data = get_token_data(user_db)

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    db_token = RefreshToken(
        user_id=user_db.id,
        token=refresh_token
    )

    db.add(db_token)
    db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@auth_router.post("/logout")
async def logout(
    refresh_token: str = Body(..., embed=True), db: Session = Depends(get_db)
):
    stored_token = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()

    if not stored_token:
        raise HTTPException(status_code=401, detail="Invalid token")

    db.delete(stored_token)
    db.commit()

    return {"message": "Successfully logged out"}


@auth_router.post("/refresh", response_model=TokenResponse)
async def refresh(refresh_token: str, db: Session = Depends(get_db)):
    stored_token = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()

    if not stored_token:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_db = db.query(User).filter(User.id == stored_token.user_id).first()

    if not user_db:
        raise HTTPException(status_code=401, detail="User not found")

    token_data = get_token_data(user_db)

    new_access_token = create_access_token(token_data)
    new_refresh_token = create_refresh_token(token_data)

    stored_token.token = new_refresh_token
    db.commit()

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer"
    )


@auth_router.get("/me", response_model=UserResponse)
async def user_me(profile: User = Depends(get_current_user)):
    return profile


@auth_router.get("/verify")
async def verify_user(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "full_name": current_user.full_name,
        "email": current_user.email
    }