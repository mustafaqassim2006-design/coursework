# services/tickets_service.py

from typing import List, Any

from DB.db import DatabaseManager
from DB.crud import (
    get_all_tickets,
    create_ticket,
    update_ticket_status,
    delete_ticket,
)


class TicketService:
    """
    Business logic for IT support tickets (it_tickets table).
    """

    def __init__(self, db_manager_cls=DatabaseManager):
        self._db_manager_cls = db_manager_cls

    def _get_db(self):
        return self._db_manager_cls()

    def list_tickets(self) -> List[Any]:
        with self._get_db() as db:
            rows = get_all_tickets(db)
        return rows

    def create_ticket(
        self,
        ticket_id: str,
        category: str,
        priority: str,
        status: str,
        opened_at: str,
        closed_at: str | None,
        assigned_to: str,
    ) -> None:
        with self._get_db() as db:
            create_ticket(
                db,
                ticket_id=ticket_id,
                category=category,
                priority=priority,
                status=status,
                opened_at=opened_at,
                closed_at=closed_at,
                assigned_to=assigned_to,
            )

    def change_status(self, ticket_id: str, new_status: str) -> None:
        with self._get_db() as db:
            update_ticket_status(db, ticket_id, new_status)

    def remove_ticket(self, ticket_id: str) -> None:
        with self._get_db() as db:
            delete_ticket(db, ticket_id)
