from typing import List

from sqlalchemy import select

from src.answer.model.answer import Answer


class AnswerRepository:
    def __init__(self, session):
        self.session = session

    def add_answer(self, answer: Answer):
        self.session.add(answer)
        self.session.flush()
        return answer

    def get_answered_case_list_by_user(self, user_email: str) -> List[str]:
        statement = (
            select(Answer.task_id)
            .select_from(Answer)
            .where(Answer.user_email == user_email)
        )
        return self.session.execute(statement).scalars().all()
