from src.cases.model.clinical_data.person.visit_occurrence import VisitOccurrence


class VisitOccurrenceRepository:
    def __init__(self, session):
        self.session = session

    def get_visit_occurrence(self, visit_id: int):
        return self.session.get(VisitOccurrence, visit_id)
