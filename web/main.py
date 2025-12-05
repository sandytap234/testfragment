from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.security import HTTPBearer
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
from jose import jwt
from datetime import datetime, timedelta
from auth import validate_telegram_data
from models import User, init_db

# === Настройки ===
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
JWT_SECRET = os.getenv("JWT_SECRET", "supersecret")
JWT_ALGO = "HS256"

# === Инициализация ===
app = FastAPI()
security = HTTPBearer()
init_db(DATABASE_URL)


# === DB Dependency ===
def get_db():
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# === Эндпоинты ===
@app.get("/", response_class=FileResponse)
async def web_app():
    return FileResponse("static/index.html")


@app.post("/auth")
async def auth(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    init_data = data.get("initData")
    if not init_data:
        raise HTTPException(400, "initData required")

    user_info = validate_telegram_data(init_data, os.getenv("BOT_TOKEN"))
    tg_id = user_info["id"]
    username = user_info.get("username", "")

    user = db.query(User).filter(User.telegram_id == tg_id).first()
    if not user:
        payload = {
            "sub": str(tg_id),
            "exp": datetime.utcnow() + timedelta(days=30)
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)
        user = User(telegram_id=tg_id, username=username, auth_token=token)
        db.add(user)
        db.commit()
    else:
        token = user.auth_token

    return {"token": token}


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(token: str = Depends(security)):
    try:
        jwt.decode(token.credentials, JWT_SECRET, algorithms=[JWT_ALGO])
        return "<h1>✅ Авторизован! Добро пожаловать в личный кабинет.</h1>"
    except:
        raise HTTPException(401, "Invalid token")