import pytest

from src.cases.repository.observation_repository import ObservationRepository
from tests.cases.case_fixture import input_case


@pytest.fixture(scope="session")
def observation_repository(session):
    return ObservationRepository(session)


def test_get_observations_by_type(
    observation_repository: ObservationRepository, session
):
    input_case(session)

    observations = observation_repository.get_observations_by_type(1, [4034855])

    assert len(observations) == 2


def test_get_observations_by_concept(
    observation_repository: ObservationRepository, session
):
    input_case(session)

    measurements = observation_repository.get_observations_by_concept(1, [4167217])

    assert len(measurements) == 5
