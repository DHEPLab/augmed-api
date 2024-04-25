import pytest

from src.cases.repository.visit_occurrence_repository import \
    VisitOccurrenceRepository
from tests.cases.case_fixture import input_case


@pytest.fixture(scope="session")
def visit_occurrence_repository(session):
    return VisitOccurrenceRepository(session)


def test_get_concept(visit_occurrence_repository: VisitOccurrenceRepository, session):
    input_case(session)

    visit = visit_occurrence_repository.get_visit_occurrence(1)

    assert visit is not None
    assert visit.person_id == 1
