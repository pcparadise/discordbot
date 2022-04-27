"""
Initial migration.
"""
import pathlib
import aiosqlite


async def run_migration(db_path: pathlib.Path):
    """
    Run migration for initial version.
    """
    async with aiosqlite.connect(db_path) as database:
        cur = await database.cursor()
        await cur.execute("CREATE TABLE metadata (version INTEGER NOT NULL)")
        await cur.execute(
            "INSERT INTO metadata VALUES (?)", [0]
        )  # the initial migration. An empty database.
        await database.commit()
