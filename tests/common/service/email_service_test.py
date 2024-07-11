
from unittest.mock import patch
import boto3
import re
import pytest
from src.common.exception.BusinessException import BusinessException, BusinessExceptionEnum
from src.common.service.email_service import send_email
from botocore.exceptions import ClientError


SUBJECT = "test_subject"
TO_ADDRESSES = ["user@test.com"]


def send_email_error(): 
    raise ClientError()


def test_send_email_failed_when_template_not_found(mocker):
    html_template_name = "no_template.html"
    data = {"link": "https://test.link"}

    with pytest.raises(BusinessException, match=re.compile(BusinessExceptionEnum.RenderTemplateError.name)):
        send_email(SUBJECT, TO_ADDRESSES, html_template_name, **data)


def test_send_email_failed(mocker):
    html_template_name = "reset_password.html"
    data = {"link": "https://test.link"}

    error_response = {'Error': {'Message': 'An error occurred'}}
    client_error = ClientError(error_response, 'send_email')

    mock_client = mocker.Mock()
    mock_client.send_email.side_effect = client_error
    mocker.patch('boto3.session.Session.client', return_value=mock_client)

    with pytest.raises(BusinessException, match=re.compile(BusinessExceptionEnum.SendEmailError.name)):
        send_email(SUBJECT, TO_ADDRESSES, html_template_name, **data)

    mock_client.send_email.assert_called_once()


def test_send_email_success(mocker):
    html_template_name = "reset_password.html"
    data = {"link": "https://test.link"}

    mock_client = mocker.Mock()
    mock_client.send_email.return_value = {
        "MessageId": "email_id"
    }
    mocker.patch('boto3.session.Session.client', return_value=mock_client)

    assert send_email(SUBJECT, TO_ADDRESSES, html_template_name, **data) == "email_id"
