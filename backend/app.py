from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
def get_db_connection():
    conn = psycopg2.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        database=os.environ.get('DB_NAME', 'quiz_db'),
        user=os.environ.get('DB_USER', 'postgres'),
        password=os.environ.get('DB_PASSWORD', 'postgres'),
        port=os.environ.get('DB_PORT', 5432)
    )
    return conn

# Initialize database
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            nickname VARCHAR(255) UNIQUE NOT NULL,
            quiz_starts_count INT DEFAULT 0,
            mistakes INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

@app.on_event("startup")
def startup_event():
   pass

class StartQuizRequest(BaseModel):
    nickname: str

@app.post("/api/quiz/start")
def start_quiz(request: StartQuizRequest):
    nickname = request.nickname.strip()
    if not nickname:
        raise HTTPException(status_code=400, detail="Nickname is required")
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        # Get or create user
        cur.execute("SELECT * FROM users WHERE nickname = %s", (nickname,))
        user = cur.fetchone()
        if not user:
            cur.execute("INSERT INTO users (nickname) VALUES (%s) RETURNING *", (nickname,))
            user = cur.fetchone()
        
        # Increment quiz_starts_count
        cur.execute("UPDATE users SET quiz_starts_count = quiz_starts_count + 1 WHERE id = %s RETURNING *", (user['id'],))
        user = cur.fetchone()
        conn.commit()
        return {"nickname": user['nickname'], "quiz_starts_count": user['quiz_starts_count'], "lives": 3 - user['mistakes']}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

class MistakeRequest(BaseModel):
    nickname: str

@app.post("/api/quiz/mistake")
def record_mistake(request: MistakeRequest):
    nickname = request.nickname.strip()
    if not nickname:
        raise HTTPException(status_code=400, detail="Nickname is required")
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("UPDATE users SET mistakes = mistakes + 1 WHERE nickname = %s RETURNING *", (nickname,))
        user = cur.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        conn.commit()
        return {"nickname": user['nickname'], "mistakes": user['mistakes'], "lives": 3 - user['mistakes']}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/api/user/{nickname}")
def get_user(nickname: str):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("SELECT * FROM users WHERE nickname = %s", (nickname,))
        user = cur.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {"nickname": user['nickname'], "quiz_starts_count": user['quiz_starts_count'], "lives": 3 - user['mistakes']}
    finally:
        cur.close()
        conn.close()
     
from fastapi.staticfiles import StaticFiles
app.mount("/", StaticFiles(directory=".", html=True), name="static")