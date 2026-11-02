import os

import aiosqlite

# Можно переопределить переменной окружения DB_PATH (например, на Railway —
# путь внутри подключённого volume, чтобы база не стиралась при редеплое).
DB_PATH = os.getenv("DB_PATH", "applications.db")


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT,
                full_name TEXT,
                game TEXT,
                subscribers TEXT,
                videos_per_day TEXT,
                goal TEXT,
                screenshot_file_id TEXT,
                status TEXT DEFAULT 'pending'
            )
            """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS blocked_users (
                user_id INTEGER PRIMARY KEY
            )
            """
        )
        await db.commit()


async def save_application(data: dict) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            INSERT INTO applications
                (user_id, username, full_name, game, subscribers,
                 videos_per_day, goal, screenshot_file_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["user_id"],
                data.get("username"),
                data.get("full_name"),
                data["game"],
                data["subscribers"],
                data["videos_per_day"],
                data["goal"],
                data["screenshot_file_id"],
            ),
        )
        await db.commit()
        return cursor.lastrowid


async def get_application(app_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM applications WHERE id = ?", (app_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def set_application_status(app_id: int, status: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE applications SET status = ? WHERE id = ?", (status, app_id)
        )
        await db.commit()


async def block_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO blocked_users (user_id) VALUES (?)", (user_id,)
        )
        await db.commit()


async def is_blocked(user_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT 1 FROM blocked_users WHERE user_id = ?", (user_id,)
        ) as cursor:
            return (await cursor.fetchone()) is not None
