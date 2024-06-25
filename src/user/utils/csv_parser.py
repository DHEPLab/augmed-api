import csv
import os
from io import StringIO
from typing import List

from src.common.exception.BusinessException import (BusinessException,
                                                    BusinessExceptionEnum)
from src.user.model.configuration import Configuration

H_USER = "User"
H_CASE = "Case No."
H_PATH = "Path"
H_COLLAPSE = "Collapse"
H_HIGHLIGHT = "Highlight"
H_TOP = "Top"


def is_empty(value):
    return value is None or value == ""


def validate_and_extract_user_case(row):
    user, case = row[H_USER], row[H_CASE]

    if not user:
        raise BusinessException(BusinessExceptionEnum.InvalidUserEmail)
    if not case:
        raise BusinessException(BusinessExceptionEnum.InvalidCaseId)

    return user, case


def validate_and_convert_case_id(case):
    try:
        return int(case)
    except (ValueError, TypeError):
        raise BusinessException(BusinessExceptionEnum.InvalidCaseId)


def validate_and_convert_top(row):
    path, top = row[H_PATH], row[H_TOP]

    if not is_empty(top):
        # The top config can not set on root node.
        if len(path.split(".")) < 2:
            raise BusinessException(BusinessExceptionEnum.ConfigFileIncorrect)
        # The top config only allow number as input.
        try:
            return float(top)
        except (ValueError, TypeError):
            raise BusinessException(BusinessExceptionEnum.ConfigFileIncorrect)


def build_style_dict(collapse, highlight, top) -> dict:
    style = {}
    if not is_empty(collapse):
        style["collapse"] = collapse
    if not is_empty(highlight):
        style["highlight"] = highlight
    if not is_empty(top):
        style["top"] = top
    return style


class CsvConfigurationParser:
    def __init__(self, csv_stream: StringIO):
        csv_reader = csv.DictReader(csv_stream, delimiter=",")
        self.csv_data = []
        for row in csv_reader:
            self.csv_data.append(row)
        self.current_config = None

    def parse(self) -> List[Configuration]:
        configurations = []

        for row in self.csv_data:
            user, case = validate_and_extract_user_case(row)
            case_id = validate_and_convert_case_id(case)
            top = validate_and_convert_top(row)

            if self._should_create_new_config(user, case_id):
                self.current_config = Configuration(
                    user_email=user, case_id=case_id, path_config=[]
                )
                configurations.append(self.current_config)

            self._process_path_config(row, top)

        return configurations

    def _should_create_new_config(self, user, case_id):
        return (
            self.current_config is None
            or self.current_config.user_email != user
            or self.current_config.case_id != case_id
        )

    def _process_path_config(self, row, top):
        path, collapse, highlight = row[H_PATH], row[H_COLLAPSE], row[H_HIGHLIGHT]

        if not is_empty(path):
            style = build_style_dict(collapse, highlight, top)
            if style:
                self.current_config.path_config.append({"path": path, "style": style})


def parse_csv_stream_to_configurations(csv_stream: StringIO) -> List[Configuration]:
    parser = CsvConfigurationParser(csv_stream)
    return parser.parse()


def is_csv_file(filename: str | None):
    if filename is None:
        return False

    _, extension = os.path.splitext(filename)
    return extension == ".csv"
