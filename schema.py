from db import DatabaseManager as DM

def create_tables(db: DM):
    c = db.cursor()
    
    # Users Table
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL
    );
    """)
    
    # Cybersecurity incidents
    c.execute("""
    CREATE TABLE IF NOT EXISTS cyber_incidents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        incident_id TEXT,
        incident_type TEXT,
        severity TEXT,
        status TEXT,
        reported_at TEXT,
        resolved_at TEXT,
        assigned_to TEXT,
        description TEXT
    );
    """)
    
    
    # Dataset metadata
    c.execute("""
    CREATE TABLE IF NOT EXISTS datasets_metadata (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dataset_name TEXT,
        owner TEXT,
        source_system TEXT,
        size_mb REAL,
        row_count INTEGER,
        created_at TEXT
    );
    """)

    # IT tickets
    c.execute("""
    CREATE TABLE IF NOT EXISTS it_tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_id TEXT,
        category TEXT,
        priority TEXT,
        status TEXT,
        opened_at TEXT,
        closed_at TEXT,
        assigned_to TEXT
    );
    """)