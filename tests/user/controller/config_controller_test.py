from io import BytesIO


def test_successful_file_upload(client, mocker):
    data = {
        'file': (BytesIO(b'content of the file'), 'test.xlsx')
    }
    mocker.patch('src.user.service.configuration_service.ConfigurationService.process_excel_file',
                 return_value={"user@example.com-1": "added"})
    mocker.patch('src.user.utils.auth_utils.validate_jwt_and_refresh', return_value=None)

    response = client.post("admin/config/upload", content_type='multipart/form-data', data=data)
    assert response.status_code == 200
    assert response.json["data"]["user@example.com-1"] == "added"


def test_no_file_part(client, mocker):
    mocker.patch('src.user.utils.auth_utils.validate_jwt_and_refresh', return_value=None)

    response = client.post("/admin/config/upload")
    assert response.status_code == 400
    assert 'NoFilePart' in response.json["error"]["message"]


def test_invalid_file_extension(client, mocker):
    data = {
        'file': (BytesIO(b'content of the file'), 'test.txt')
    }
    mocker.patch('src.user.utils.auth_utils.validate_jwt_and_refresh', return_value=None)

    response = client.post("/admin/config/upload", content_type='multipart/form-data', data=data)
    assert response.status_code == 400
    assert 'InvalidFileExtension' in response.json["error"]["message"]


def test_error_during_file_processing(client, mocker):
    data = {
        'file': (BytesIO(b'content of the file'), 'test.xlsx')
    }
    mocker.patch('src.user.service.configuration_service.ConfigurationService.process_excel_file',
                 side_effect=Exception("Processing failed"))
    mocker.patch('src.user.utils.auth_utils.validate_jwt_and_refresh', return_value=None)

    response = client.post("/admin/config/upload", content_type='multipart/form-data', data=data)
    assert response.status_code == 500
