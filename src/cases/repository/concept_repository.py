from src.cases.model.vocabularies.concept import Concept


class ConceptRepository:
    def __init__(self, session):
        self.session = session

    def get_concept(self, concept_id: int) -> Concept:
        return self.session.get(Concept, concept_id)
