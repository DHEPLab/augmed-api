from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.answer.model.answer import Answer


class AnswerRepository:
    """
    Persists Answer rows.

    Key fix: add_answer() commits the session so the row survives the request.
    """

    def __init__(self, session: Session):  # pragma: no cover
        self.session = session

    # ------------------------------------------------------------------ #
    def add_answer(self, answer: Answer) -> Answer:  # pragma: no cover
        """
        Insert + commit.  Returns the persisted Answer instance.
        """
        self.session.add(answer)
        self.session.commit()
        return answer

    # ------------------------------------------------------------------ #
    def get_answered_case_list_by_user(self, user_email: str) -> List[str]:
        statement = (
            select(Answer.task_id)
            .select_from(Answer)
            .where(Answer.user_email == user_email)
        )
        return self.session.execute(statement).scalars().all()
