from datetime import datetime
import uuid
from flask import json
import pytest

from src.common.exception.BusinessException import BusinessException, BusinessExceptionEnum
from src.configration.model.answer_config import AnswerConfig

# @pytest.fixture(autouse=True)
# def before_each_tests(mocker):
#     mocker.patch('src.user.utils.auth_utils.validate_jwt_and_refresh', return_value=None)

@pytest.fixture()
def test_config():
    return [{
        "type": "Text",
        "title": "Please make a diagosis"
    }]


def test_add_answer_config_success(client, mocker, test_config):  
    id = uuid.uuid4()

    mocker.patch(
        'src.configration.service.answer_service.AnswerConfigurationService.add_new_answer_config',
        return_value=id
    )

    response = client.post("/admin/config/answer", data=json.dumps(test_config), content_type='application/json')

    assert response.status_code == 200
    assert {
        "data": {
            "id": str(id)
        },
        "error": None
    } == response.json


def test_add_answer_config_failed_by_empty_config(client):
    empty_config = []

    response = client.post("/admin/config/answer", data=json.dumps(empty_config), content_type='application/json')

    assert response.status_code == 500
    assert {
        "data": None,
        "error": {'code': '1020', 'message': 'Invalid answer config. Error:Answer config can not be empty list.'}
    } == response.json


def test_get_latest_answer_config_success(client, mocker, test_config):
    answer_config = AnswerConfig(
        id=uuid.uuid4(),
        config=test_config,
        created_timestamp=datetime.now()
    )

    mocker.patch(
        'src.configration.service.answer_service.AnswerConfigurationService.get_latest_answer_config',
        return_value=answer_config
    )

    response = client.get("/api/config/answer", data=json.dumps(test_config), content_type='application/json')

    assert response.status_code == 200
    assert {
        'data': answer_config.to_dict(),
        'error': None
    } == response.json


def test_get_latest_answer_config_failed_by_no_answer_config(client, mocker, test_config):
    mocker.patch(
        'src.configration.service.answer_service.AnswerConfigurationService.get_latest_answer_config',
        side_effect=BusinessException(BusinessExceptionEnum.NoAnswerConfigAvailable)
    )

    response = client.get("/api/config/answer", data=json.dumps(test_config), content_type='application/json')

    assert response.status_code == 500
    assert {
        'data': None,
        'error': {
            'code': '1021',
            'message': 'No answer config available. Please configure it first.',
        }
    } == response.json
