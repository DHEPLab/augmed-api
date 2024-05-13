
import pytest

from src.diagnose.model.diagnose import Diagnose
from src.diagnose.repository.diagnose_repository import DiagnoseRepository


@pytest.fixture(scope="session")
def diagonose_repository(session):
    return DiagnoseRepository(session)


def test_add_diagonose(diagonose_repository):
    diagnose = Diagnose(task_id=1,
                        case_id=1,
                        user_email="user@test.com",
                        display_configuration=[],
                        diagnosis=[],
                        other=""
                        )

    assert diagnose.id is None

    diagonose_repository.add_diagonose(diagnose)

    assert diagnose.id is not None
