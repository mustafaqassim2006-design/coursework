# services/incidents_service.py

from typing import List, Any

from DB.db import DatabaseManager
from DB.crud import (
    get_all_incidents,
    create_incident,
    update_incident_status,
    delete_incident,
)


class IncidentService:
    """
    Business logic for cybersecurity incidents.
    Streamlit pages use this instead of calling CRUD functions directly.
    """

    def __init__(self, db_manager_cls=DatabaseManager):
        self._db_manager_cls = db_manager_cls

    def _get_db(self):
        return self._db_manager_cls()

    # --------- Queries ---------

    def list_incidents(self) -> List[Any]:
        with self._get_db() as db:
            rows = get_all_incidents(db)
        return rows

    # --------- Commands ---------

    def create_incident(
        self,
        incident_id: str,
        incident_type: str,
        severity: str,
        status: str,
        reported_at: str,
        resolved_at: str | None,
        assigned_to: str,
        description: str,
    ) -> None:
        with self._get_db() as db:
            create_incident(
                db,
                incident_id=incident_id,
                incident_type=incident_type,
                severity=severity,
                status=status,
                reported_at=reported_at,
                resolved_at=resolved_at,
                assigned_to=assigned_to,
                description=description,
            )

    def change_status(self, incident_id: str, new_status: str) -> None:
        with self._get_db() as db:
            update_incident_status(db, incident_id, new_status)

    def remove_incident(self, incident_id: str) -> None:
        with self._get_db() as db:
            delete_incident(db, incident_id)
