import sqlite3
from pathlib import Path

DATA_DIR = Path("c:\MDX CSSE\Mustafa\My_Work\DATA")
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "intelligence_platform.db"

class DatabaseManager:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        
    def cursor(self):
        return self.conn.cursor()
    
    def commit(self):
        self.conn.commit()
        
    def close(self):
        self.conn.close()
        
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc, tb):
        if exc_type is None:
            self.commit()
        self.close()