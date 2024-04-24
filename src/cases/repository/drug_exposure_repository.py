from sqlalchemy import select

from src.cases.model.clinical_data.person.drug_exposure import DrugExposure


class DrugExposureRepository:
    def __init__(self, session):
        self.session = session

    def get_drugs(self, visit_id: int):
        statement = (
            select(DrugExposure)
            .select_from(DrugExposure)
            .where(DrugExposure.visit_occurrence_id == visit_id)
        )
        return self.session.execute(statement).scalars().all()
