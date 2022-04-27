"""
Migration version 1
"""
import pathlib
import aiosqlite


async def run_migration(db_path: pathlib.Path):
    """
    Run a migration for version 1.
    """
    async with aiosqlite.connect(db_path) as database:
        cur = await database.cursor()
        await cur.execute("CREATE TABLE servers (id INTEGER PRIMARY KEY NOT NULL)")
        await cur.execute(
            "UPDATE metadata SET version = ?", [1]
        )  # the initial migration. An empty database.
        await database.commit()
