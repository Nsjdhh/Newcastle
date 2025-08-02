import aiosqlite

DB_NAME = "evolution.db"

async def create_tables():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            age INTEGER,
            city TEXT,
            balance INTEGER DEFAULT 0,
            job TEXT DEFAULT '',
            car TEXT DEFAULT '',
            house TEXT DEFAULT ''
        )
        """)
        await db.commit()

async def add_user(user_id: int, first_name: str, last_name: str, age: int, city: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        INSERT OR REPLACE INTO users (user_id, first_name, last_name, age, city, balance)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, first_name, last_name, age, city, 5000))  # стартовый баланс
        await db.commit()

async def get_user(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchone()
