from src.database import Database

with Database("Chinook_Sqlite.sqlite") as db:
    print(db.object_names)
