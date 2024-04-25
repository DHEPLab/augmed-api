import pytest

from src.cases.repository.concept_repository import ConceptRepository
from tests.cases.case_fixture import input_case


@pytest.fixture(scope="session")
def concept_repository(session):
    return ConceptRepository(session)


def test_get_concept(concept_repository: ConceptRepository, session):
    input_case(session)

    found = concept_repository.get_concept(2)

    assert found is not None
    assert found.concept_name == "M"
