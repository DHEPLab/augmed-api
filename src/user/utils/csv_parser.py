import csv
import os
from io import StringIO
from typing import List

from src.common.exception.BusinessException import (BusinessException,
                                                    BusinessExceptionEnum)
from src.user.model.configuration import Configuration


class CsvConfigurationParser:
    def __init__(self, excel_stream: StringIO):
        csv_reader = csv.reader(excel_stream, delimiter=",")
        next(csv_reader)
        self.csv_data = []
        for row in csv_reader:
            self.csv_data.append([cell if cell != "" else None for cell in row])

    def parse(self) -> List[Configuration]:
        configurations = []
        current_config = None

        for row in self.csv_data:
            if not any(cell is not None for cell in row):
                continue
            user, case = self._validate_and_extract_user_case(row)
            case_id = self._validate_and_convert_case_id(case)

            self._validate_path_and_top(row)

            if self._should_create_new_config(current_config, user, case_id):
                current_config = self._create_new_config(user, case_id)
                configurations.append(current_config)

            self._process_path_config(current_config, row)

        return configurations

    def _validate_and_extract_user_case(self, row):
        user = row[0]
        case = row[1]

        if not user:
            raise BusinessException(BusinessExceptionEnum.InvalidUserEmail)

        if not case:
            raise BusinessException(BusinessExceptionEnum.InvalidCaseId)

        return user, case

    def _validate_and_convert_case_id(self, case):
        try:
            return int(case)
        except (ValueError, TypeError):
            raise BusinessException(BusinessExceptionEnum.InvalidCaseId)

    def _validate_path_and_top(self, row):
        path = row[2]
        top = row[5]

        if top is not None:
            # The top config only allow number as input.
            if not isinstance(top, (int, float)):
                raise BusinessException(BusinessExceptionEnum.ConfigFileIncorrect)
            # The top config can not set on root node.
            if len(str(path).split(".")) < 2:
                raise BusinessException(BusinessExceptionEnum.ConfigFileIncorrect)

    def _should_create_new_config(self, current_config, user, case_id):
        return (
            not current_config
            or current_config.user_email != user
            or current_config.case_id != case_id
        )

    def _create_new_config(self, user, case_id):
        return Configuration(user_email=user, case_id=case_id, path_config=[])

    def _process_path_config(self, current_config, row):
        path = row[2]
        collapse = row[3]
        highlight = row[4]
        top = row[5]

        if path:
            style = self._build_style_dict(collapse, highlight, top)
            if style:
                current_config.path_config.append({"path": path, "style": style})

    def _build_style_dict(self, collapse, highlight, top) -> dict:
        style = {}
        if collapse is not None:
            style["collapse"] = collapse
        if highlight is not None:
            style["highlight"] = highlight
        if top is not None:
            style["top"] = top
        return style


def parse_csv_stream_to_configurations(excel_stream: StringIO) -> List[Configuration]:
    parser = CsvConfigurationParser(excel_stream)
    return parser.parse()


def is_csv_file(filename: str | None):
    if filename is None:
        return False

    _, extension = os.path.splitext(filename)
    return extension == ".csv"
