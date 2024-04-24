from sqlalchemy import select

from src.cases.model.clinical_data.person.observation import Observation


class ObservationRepository:
    def __init__(self, session):
        self.session = session

    def get_observations_by_type(self, visit_id: int, concept_type_ids):
        statement = (
            select(Observation)
            .select_from(Observation)
            .where(
                Observation.observation_type_concept_id.in_(concept_type_ids),
                Observation.visit_occurrence_id == visit_id,
            )
        )
        return self.session.execute(statement).scalars().all()

    def get_observations_by_concept(self, visit_id: int, concept_ids):
        statement = (
            select(Observation)
            .select_from(Observation)
            .where(
                Observation.observation_concept_id.in_(concept_ids),
                Observation.visit_occurrence_id == visit_id,
            )
        )
        return self.session.execute(statement).scalars().all()
