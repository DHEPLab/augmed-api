from typing import List

from sqlalchemy import select

from src.diagnose.model.diagnose import Diagnose


class DiagnoseRepository:
    def __init__(self, session):
        self.session = session

    def add_diagnose(self, diagnose: Diagnose):
        self.session.add(diagnose)
        self.session.flush()
        return diagnose

    def get_diagnosed_case_list_by_user(self, user_email: str) -> List[str]:
        statement = (
            select(Diagnose.task_id)
            .select_from(Diagnose)
            .where(Diagnose.user_email == user_email)
        )
        return self.session.execute(statement).scalars().all()
