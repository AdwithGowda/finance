from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel
from typing import List
import os

app = FastAPI(title="Finance API")

# -------------------- CORS --------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- DATABASE --------------------
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

def get_connection():
    return psycopg2.connect(
        DATABASE_URL,
        sslmode="require"  # REQUIRED for Render PostgreSQL
    )

# -------------------- MODELS --------------------
class Expense(BaseModel):
    title: str
    amount: float
    category: str

class ExpenseOut(Expense):
    id: int
    date_created: str

# -------------------- STARTUP: CREATE TABLE --------------------
@app.on_event("startup")
def create_table():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS expenses (
                        id SERIAL PRIMARY KEY,
                        title TEXT NOT NULL,
                        amount NUMERIC NOT NULL,
                        category TEXT NOT NULL,
                        date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                conn.commit()
        print("✅ expenses table ready")
    except Exception as e:
        print("❌ Table creation failed:", e)

# -------------------- HEALTH CHECK --------------------
@app.get("/")
def health():
    return {"status": "ok"}

# -------------------- ROUTES --------------------
@app.get("/expenses", response_model=List[ExpenseOut])
def get_expenses():
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT id, title, amount, category, date_created
                    FROM expenses
                    ORDER BY date_created DESC
                """)
                return cur.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/expenses", status_code=status.HTTP_201_CREATED)
def add_expense(expense: Expense):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO expenses (title, amount, category)
                    VALUES (%s, %s, %s)
                    RETURNING id
                    """,
                    (expense.title, expense.amount, expense.category)
                )
                expense_id = cur.fetchone()[0]
                conn.commit()
                return {"status": "success", "id": expense_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/expenses/{expense_id}")
def update_expense(expense_id: int, expense: Expense):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE expenses
                    SET title=%s, amount=%s, category=%s
                    WHERE id=%s
                    """,
                    (expense.title, expense.amount, expense.category, expense_id)
                )
                if cur.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Expense not found")
                conn.commit()
                return {"status": "updated"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM expenses WHERE id=%s",
                    (expense_id,)
                )
                if cur.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Expense not found")
                conn.commit()
                return {"status": "deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
