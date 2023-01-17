"""
Migration version 3
"""
import pathlib
import aiosqlite


async def run_migration(db_path: pathlib.Path):
    """
    Run a migration for version 3.
    """
    async with aiosqlite.connect(db_path) as database:
        cur = await database.cursor()
        create_welcome_config_settings = (
            "CREATE TABLE welcome_config_settings ("
            "    server_id INTEGER PRIMARY KEY,"
            "    detection_word TEXT NOT NULL,"
            "    role_id INTEGER NOT NULL,"
            "    welcome_channel_id INTEGER NOT NULL"
            ");"
        )

        await cur.execute(create_welcome_config_settings)
        await cur.execute(
            "UPDATE metadata SET version = ?", [3]
        )  # the initial migration. An empty database.
        await database.commit()
