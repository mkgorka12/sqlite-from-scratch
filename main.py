from src.database.database import Database

with Database("Chinook_Sqlite.sqlite") as db:
    page_content = db.get_page_content(1)
    print(page_content)
