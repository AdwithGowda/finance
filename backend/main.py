from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel
import os

app = FastAPI()

# Enable CORS for React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load DATABASE_URL from environment (Render)
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

class Expense(BaseModel):
    title: str
    amount: float
    category: str

def get_connection():
    return psycopg2.connect(
        DATABASE_URL,
        sslmode="require"  # REQUIRED for Render PostgreSQL
    )

@app.get("/expenses")
def get_expenses():
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT id, title, amount, category, date_created
            FROM expenses
            ORDER BY date_created DESC
        """)
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
            (expense.title, expense.amount, expense.category)
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
            """
            UPDATE expenses
            SET title=%s, amount=%s, category=%s
            WHERE id=%s
            """,
            (expense.title, expense.amount, expense.category, expense_id)
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
