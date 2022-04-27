"""
A module for running migrations on our database.
"""
import pathlib
import importlib
import sqlite3
import aiosqlite


class _Migration:  # pylint: disable=too-few-public-methods
    """
    A type stub for a migration module.
    """

    @staticmethod
    async def run_migration(_: pathlib.Path):
        """
        runs the migration to go up one database version.
        """


def _load_migration(name: str) -> _Migration:
    """
    Type stub so importlib.import_module will be well typed.
    """
    return importlib.import_module(f".{name}", package=__package__)  # type: ignore


async def run_migrations():
    """
    Run migrations on all our stuff.
    """
    program_path = pathlib.Path(__file__).absolute().parent.parent
    db_path = program_path / "database.db"
    version = None
    async with aiosqlite.connect(db_path) as database:
        cur = await database.cursor()
        try:
            await cur.execute("SELECT version FROM metadata")
            version = await cur.fetchone()
            version = version[0] if version else -1
        except sqlite3.OperationalError:
            version = -1

    imports = set(p.name for p in pathlib.Path(__file__).parent.glob("_*.py"))
    while True:
        file_name = f"_{version + 1}.py"
        if file_name in imports:
            print(file_name)
            await _load_migration(file_name[:-3]).run_migration(db_path)
            version += 1
        else:
            break
