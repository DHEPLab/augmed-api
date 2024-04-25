import pytest

from src.cases.repository.drug_exposure_repository import \
    DrugExposureRepository
from tests.cases.case_fixture import input_case


@pytest.fixture(scope="session")
def drug_exposure_repository(session):
    return DrugExposureRepository(session)


def test_get_drugs_by_visit_id(
    drug_exposure_repository: DrugExposureRepository, session
):
    input_case(session)

    drugs = drug_exposure_repository.get_drugs(1)

    assert len(drugs) == 2
