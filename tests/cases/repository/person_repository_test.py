import pytest

from src.cases.repository.person_repository import PersonRepository
from tests.cases.case_fixture import input_case


@pytest.fixture(scope="session")
def person_repository(session):
    return PersonRepository(session)


def test_get_concept(person_repository: PersonRepository, session):
    input_case(session)

    person = person_repository.get_person(1)

    assert person is not None
    assert person.gender_concept_id == 2
