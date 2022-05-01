"""
Migration version 2
"""
import pathlib
import aiosqlite


async def run_migration(db_path: pathlib.Path):
    """
    Run a migration for version 2.
    """
    async with aiosqlite.connect(db_path) as database:
        cur = await database.cursor()
        create_activity_tracking_settings = (
            "CREATE TABLE activity_tracking_settings ("
            "    id INTEGER PRIMARY KEY NOT NULL,"
            "    server_id INTEGER NOT NULL,"
            "    time_period INTEGER NOT NULL,"
            "    role_id INTEGER NOT NULL,"
            "    message_count INTEGER NOT NULL,"
            "    FOREIGN KEY(server_id) REFERENCES servers(id)"
            ");"
        )
        create_activity_tracking_channels = (
            "CREATE TABLE activity_tracking_channels ("
            "    channel INTEGER NOT NULL,"
            "    activity_tracking_id INTEGER NOT NULL,"
            "    FOREIGN KEY(activity_tracking_id)"
            "       REFERENCES activity_tracking_settings(activity_tracking_id)"
            ");"
        )
        create_message_log = (
            "CREATE TABLE message_log ("
            "    channel_id INTEGER NOT NULL,"
            "    user_id INTEGER NOT NULL,"
            "    time INTEGER NOT NULL,"
            "    server_id INTEGER NOT NULL,"
            "    FOREIGN KEY(server_id) REFERENCES servers(id)"
            ");"
        )
        await cur.execute(create_activity_tracking_settings)
        await cur.execute(create_activity_tracking_channels)
        await cur.execute(create_message_log)
        await cur.execute(
            "UPDATE metadata SET version = ?", [2]
        )  # the initial migration. An empty database.
        await database.commit()
