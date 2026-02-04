from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

app = FastAPI()

@app.get("/")
def root():
    return {"status": "MyWallet API running"}
# Enable CORS for React
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://finance-1-wt2p.onrender.com",  # React frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Read DATABASE_URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not found in environment variables")

# -------------------- MODELS --------------------

class Expense(BaseModel):
    title: str
    amount: float
    category: str

# -------------------- DB CONNECTION --------------------

def get_connection():
    return psycopg2.connect(
        DATABASE_URL,
        sslmode="require"
    )


# -------------------- TABLE CREATION --------------------

def create_expenses_table():
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                amount NUMERIC(10,2) NOT NULL,
                category TEXT NOT NULL,
                date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cur.close()
        print("✅ expenses table checked/created")
    except Exception as e:
        print("❌ Error creating table:", e)
    finally:
        if conn:
            conn.close()

@app.on_event("startup")
def startup_event():
    create_expenses_table()

# -------------------- ROUTES --------------------

@app.get("/expenses")
def get_expenses():
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(
            "SELECT id, title, amount, category, date_created FROM expenses ORDER BY id DESC"
        )
        data = cur.fetchall()
        cur.close()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()

@app.post("/expenses")
def add_expense(expense: Expense):
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO expenses (title, amount, category) VALUES (%s, %s, %s)",
            (expense.title, expense.amount, expense.category),
        )
        conn.commit()
        cur.close()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()

@app.put("/expenses/{expense_id}")
def update_expense(expense_id: int, expense: Expense):
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE expenses SET title=%s, amount=%s, category=%s WHERE id=%s",
            (expense.title, expense.amount, expense.category, expense_id),
        )
        conn.commit()
        cur.close()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()

@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int):
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM expenses WHERE id = %s", (expense_id,))
        conn.commit()
        cur.close()
        return {"status": "deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()
# -------------------- END OF FILE --------------------
