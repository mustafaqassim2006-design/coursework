# services/datasets_service.py

from typing import List, Any

from DB.db import DatabaseManager
from DB.crud import (
    get_all_datasets,
    create_dataset,
    update_dataset_owner,
    delete_dataset,
)


class DatasetService:
    """
    Business logic for data assets (datasets_metadata table).
    """

    def __init__(self, db_manager_cls=DatabaseManager):
        self._db_manager_cls = db_manager_cls

    def _get_db(self):
        return self._db_manager_cls()

    def list_datasets(self) -> List[Any]:
        with self._get_db() as db:
            rows = get_all_datasets(db)
        return rows

    def register_dataset(
        self,
        dataset_name: str,
        owner: str,
        source_system: str,
        size_mb: float,
        row_count: int,
        created_at: str,
    ) -> None:
        with self._get_db() as db:
            create_dataset(
                db,
                dataset_name=dataset_name,
                owner=owner,
                source_system=source_system,
                size_mb=size_mb,
                row_count=row_count,
                created_at=created_at,
            )

    def change_owner(self, dataset_name: str, new_owner: str) -> None:
        with self._get_db() as db:
            update_dataset_owner(db, dataset_name, new_owner)

    def remove_dataset(self, dataset_name: str) -> None:
        with self._get_db() as db:
            delete_dataset(db, dataset_name)
