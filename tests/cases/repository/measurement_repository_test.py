import pytest

from src.cases.repository.measurement_repository import MeasurementRepository
from tests.cases.case_fixture import input_case


@pytest.fixture(scope="session")
def measurement_repository(session):
    return MeasurementRepository(session)


def test_get_measurements(measurement_repository: MeasurementRepository, session):
    input_case(session)

    measurements = measurement_repository.get_measurements(1, [4152368])

    assert len(measurements) == 1
    assert measurements[0].value_as_number == 10


def test_get_measurements_of_parents(
    measurement_repository: MeasurementRepository, session
):
    input_case(session)

    measurements = measurement_repository.get_measurements_of_parents(1, [4263222])

    assert len(measurements) == 2
