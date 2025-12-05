from pathlib import Path
from .db import DatabaseManager 

# USERS 
def insert_user(db : DatabaseManager, username: str, password_hash: str, role: str):
    c = db.cursor()
    c.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", (username, password_hash, role))
    
def get_user_by_username(db : DatabaseManager, username:str):
    c = db.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    
    return c.fetchone()


# Cyber Incidents

def create_incident(db: DatabaseManager, incident_id, incident_type,
                    severity, status, reported_at, resolved_at, assigned_to, description):
    c = db.cursor()
    c.execute("""
        INSERT INTO cyber_incidents
        (incident_id, incident_type, severity, status, reported_at, resolved_at, assigned_to, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (incident_id, incident_type, severity, status, reported_at, resolved_at, assigned_to, description))

def get_all_incidents(db: DatabaseManager):
    c = db.cursor()
    c.execute("SELECT * FROM cyber_incidents")
    return c.fetchall()

def update_incident_status(db: DatabaseManager, incident_id, new_status):
    c = db.cursor()
    c.execute("""
        UPDATE cyber_incidents
        SET status = ?
        WHERE incident_id = ?
    """, (new_status, incident_id))

def delete_incident(db: DatabaseManager, incident_id):
    c = db.cursor()
    c.execute("DELETE FROM cyber_incidents WHERE incident_id = ?", (incident_id,))
    
# DATASETS

def create_dataset(db: DatabaseManager, dataset_name, owner, source_system,
                   size_mb, row_count, created_at):
    c = db.cursor()
    c.execute("""
        INSERT INTO datasets_metadata
        (dataset_name, owner, source_system, size_mb, row_count, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (dataset_name, owner, source_system, size_mb, row_count, created_at))

def get_all_datasets(db: DatabaseManager):
    c = db.cursor()
    c.execute("SELECT * FROM datasets_metadata")
    return c.fetchall()

def update_dataset_owner(db: DatabaseManager, dataset_name, new_owner):
    c = db.cursor()
    c.execute("""
        UPDATE datasets_metadata
        SET owner = ?
        WHERE dataset_name = ?
    """, (new_owner, dataset_name))

def delete_dataset(db: DatabaseManager, dataset_name):
    c = db.cursor()
    c.execute("DELETE FROM datasets_metadata WHERE dataset_name = ?", (dataset_name,))


# IT TICKETS

def create_ticket(db: DatabaseManager, ticket_id, category, priority,
                  status, opened_at, closed_at, assigned_to):
    c = db.cursor()
    c.execute("""
        INSERT INTO it_tickets
        (ticket_id, category, priority, status, opened_at, closed_at, assigned_to)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (ticket_id, category, priority, status, opened_at, closed_at, assigned_to))

def get_all_tickets(db: DatabaseManager):
    c = db.cursor()
    c.execute("SELECT * FROM it_tickets")
    return c.fetchall()

def update_ticket_status(db: DatabaseManager, ticket_id, new_status):
    c = db.cursor()
    c.execute("""
        UPDATE it_tickets
        SET status = ?
        WHERE ticket_id = ?
    """, (new_status, ticket_id))

def delete_ticket(db: DatabaseManager, ticket_id):
    c = db.cursor()
    c.execute("DELETE FROM it_tickets WHERE ticket_id = ?", (ticket_id,))
