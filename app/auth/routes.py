from fastapi import APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends
from passlib.context import CryptContext
from datetime import datetime
from app.auth.dependencies import get_current_user
from app.db.mongodb import users_collection
from app.db.schemas import UserCreate
from app.auth.jwt_handler import create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


@router.post("/register", status_code=201)
async def register(user: UserCreate):
    # check duplicate
    existing = await users_collection.find_one({"username": user.username})
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    existing_email = await users_collection.find_one({"email": user.email})
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_doc = {
        "username": user.username,
        "email": user.email,
        "hashed_password": hash_password(user.password),
        "role": user.role,           # "user" or "admin"
        "created_at": datetime.utcnow()
    }
    await users_collection.insert_one(user_doc)
    return {"message": f"User '{user.username}' registered successfully"}


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await users_collection.find_one({"username": form_data.username})
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    token = create_access_token(data={
        "sub": user["username"],
        "role": user["role"]
    })
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user["role"]
    }


@router.get("/me")
async def get_me(current_user=Depends(get_current_user)):   # clean now
    return {
        "username": current_user["username"],
        "email": current_user["email"],
        "role": current_user["role"]
    }