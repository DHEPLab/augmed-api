import uuid
from flask import json
import pytest

from src.common.exception.BusinessException import BusinessException, BusinessExceptionEnum
from src.diagnose.model.diagnose import Diagnose


@pytest.fixture(autouse=True)
def before_each_tests(mocker):
    mocker.patch('src.user.utils.auth_utils.validate_jwt_and_refresh', return_value=None)


@pytest.fixture()
def fake_request_body_data(mocker):
    return {
        "answerConfigId": uuid.uuid4(),
        "answer": {"question": "answer"}
    }


def test_save_diagnose_success(client, mocker, fake_request_body_data):
    task_id = 'd523b88ae897538795ccfdb7c978b38f'

    mocker.patch(
        'src.diagnose.service.diagnose_service.DiagnoseService.add_diagnose_response',
        return_value=Diagnose(id=1)
    )

    response = client.post(f"/api/diagnose/{task_id}", data=json.dumps(fake_request_body_data), content_type='application/json')

    assert response.status_code == 200
    assert {
        "data": {
            "id": 1
        },
        "error": None
    } == response.json


def test_save_diagnose_fail(client, mocker, fake_request_body_data):
    task_id = 'd523b88ae897538795ccfdb7c978b38f'

    mocker.patch(
        'src.diagnose.service.diagnose_service.DiagnoseService.add_diagnose_response',
        side_effect=BusinessException(BusinessExceptionEnum.NoAccessToCaseReview)
    )

    response = client.post(f"/api/diagnose/{task_id}", data=json.dumps(fake_request_body_data), content_type='application/json')

    assert response.status_code == 500
    assert {
        "data": None,
        "error": {'code': '1010', 'message': 'No access to review case.'}
    } == response.json


def test_save_diagnose_fail_with_no_answer_config(client, mocker, fake_request_body_data):
    task_id = 'd523b88ae897538795ccfdb7c978b38f'

    mocker.patch(
        'src.diagnose.service.diagnose_service.DiagnoseService.add_diagnose_response',
        side_effect=BusinessException(BusinessExceptionEnum.NoAnswerConfigAvailable)
    )

    response = client.post(f"/api/diagnose/{task_id}", data=json.dumps(fake_request_body_data), content_type='application/json')

    assert response.status_code == 500
    assert {
        "data": None,
        "error": {'code': '1021', 'message': 'No answer config available. Please configure it first.'}
    } == response.json

