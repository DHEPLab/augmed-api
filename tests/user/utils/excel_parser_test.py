from io import BytesIO

from openpyxl import Workbook

from src.user.utils.excel_parser import parse_excel_stream_to_configurations


def test_should_parse_excell_stream_correctly_when_all_config_are_set():
    # Prepare the test data (Workbook with multiple configurations)
    wb = Workbook()
    ws = wb.active
    # Headers
    ws.append(['User', 'Case No.', 'Path', 'Collapse', 'Highlight'])
    # Data for multiple users and cases
    ws.append(['usera@example.com', '1', 'Background.abc', True, True])
    ws.append([None, None, 'background.xxx', True, False])
    ws.append(['userb@example.com', '1', 'Background.patient demo', False, False])
    excel_stream = BytesIO()
    wb.save(excel_stream)
    excel_stream.seek(0)

    result = parse_excel_stream_to_configurations(excel_stream)

    assert len(result) == 2

    assert result[0].user_email == 'usera@example.com'
    assert result[0].case_id == 1
    assert len(result[0].path_config) == 2
    assert result[0].path_config[0]['path'] == 'Background.abc'
    assert result[0].path_config[0]['style']['collapse'] is True
    assert result[0].path_config[0]['style']['highlight'] is True

    assert result[0].path_config[1]['path'] == 'background.xxx'
    assert result[0].path_config[1]['style']['collapse'] is True
    assert result[0].path_config[1]['style']['highlight'] is False

    assert result[1].user_email == 'userb@example.com'
    assert result[1].case_id == 1
    assert len(result[1].path_config) == 1

    assert result[1].path_config[0]['path'] == 'Background.patient demo'
    assert result[1].path_config[0]['style']['collapse'] is False
    assert result[1].path_config[0]['style']['highlight'] is False


def test_should_ignore_none_config():
    # Prepare the test data (Workbook with multiple configurations)
    wb = Workbook()
    ws = wb.active
    # Headers
    ws.append(['User', 'Case No.', 'Path', 'Collapse', 'Highlight'])
    # Data for multiple users and cases
    ws.append(['usera@example.com', '1', 'Background.abc', None, True])
    ws.append([None, None, 'background.xxx', True, None])
    ws.append([None, None, 'Background.patient demo', None, None])
    excel_stream = BytesIO()
    wb.save(excel_stream)
    excel_stream.seek(0)

    result = parse_excel_stream_to_configurations(excel_stream)

    assert len(result) == 1
    assert result[0].user_email == 'usera@example.com'
    assert result[0].case_id == 1
    assert len(result[0].path_config) == 2
    assert result[0].path_config[0]['path'] == 'Background.abc'
    assert 'Collapse' not in result[0].path_config[0]['style']
    assert result[0].path_config[0]['style']['highlight'] is True
    assert result[0].path_config[1]['path'] == 'background.xxx'
    assert result[0].path_config[1]['style']['collapse'] is True
    assert 'Highlight' not in result[0].path_config[1]['style']


def test_should_ignore_none_config_while_keep_user_case_relationship():
    # Prepare the test data (Workbook with multiple configurations)
    wb = Workbook()
    ws = wb.active
    # Headers
    ws.append(['User', 'Case No.', 'Path', 'Collapse', 'Highlight'])
    # Data for multiple users and cases
    ws.append(['usera@example.com', '1', 'Background.patient demo', None, None])
    excel_stream = BytesIO()
    wb.save(excel_stream)
    excel_stream.seek(0)

    result = parse_excel_stream_to_configurations(excel_stream)
    assert len(result) == 1
    assert result[0].user_email == 'usera@example.com'
    assert result[0].case_id == 1
    assert len(result[0].path_config) == 0


def test_should_ignore_blank_line():
    # Prepare the test data (Workbook with multiple configurations)
    wb = Workbook()
    ws = wb.active
    # Headers
    ws.append(['User', 'Case No.', 'Path', 'Collapse', 'Highlight'])
    # Data for multiple users and cases
    ws.append(['usera@example.com', '1', 'Background.patient demo', None, None])
    ws.append([None, None, None, None, None])
    excel_stream = BytesIO()
    wb.save(excel_stream)
    excel_stream.seek(0)

    result = parse_excel_stream_to_configurations(excel_stream)

    assert len(result) == 1
    assert result[0].user_email == 'usera@example.com'
    assert result[0].case_id == 1
    assert len(result[0].path_config) == 0


def test_should_keep_duplicate_user_case_relationship():
    # Prepare the test data (Workbook with multiple configurations)
    wb = Workbook()
    ws = wb.active
    # Headers
    ws.append(['User', 'Case No.', 'Path', 'Collapse', 'Highlight'])
    # Data for multiple users and cases
    ws.append(['usera@example.com', '1', 'Background.patient demo', None, None])
    ws.append(['usera@example.com', '1', 'Background.patient demo', None, None])
    ws.append([None, None, 'Background.drug', None, None])
    ws.append(['usera@example.com', '1', None, None, None])

    excel_stream = BytesIO()
    wb.save(excel_stream)
    excel_stream.seek(0)

    result = parse_excel_stream_to_configurations(excel_stream)

    assert len(result) == 3
    assert result[0].user_email == 'usera@example.com'
    assert result[0].case_id == 1
    assert len(result[0].path_config) == 0

    assert result[1].user_email == 'usera@example.com'

    assert result[1].case_id == 1
    assert len(result[1].path_config) == 0
    assert result[1].user_email == 'usera@example.com'

    assert result[2].case_id == 1
    assert len(result[1].path_config) == 0
    assert result[2].user_email == 'usera@example.com'