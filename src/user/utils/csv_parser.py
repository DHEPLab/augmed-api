import csv
import os
from io import StringIO
from typing import List, Dict, Tuple

from src.common.exception.BusinessException import (
    BusinessException,
    BusinessExceptionEnum,
)
from src.user.model.display_config import DisplayConfig

H_USER = "User"
H_CASE = "Case No."
H_PATH = "Path"
H_COLLAPSE = "Collapse"
H_HIGHLIGHT = "Highlight"
H_TOP = "Top"


def is_empty(value):
    return value is None or value == ""


def str_to_bool(value: str) -> bool:
    return value.lower() == "true"


def validate_and_extract_user_case(row: Dict[str, str]) -> Tuple[str, int]:
    user = row.get(H_USER, "").strip()
    case = row.get(H_CASE, "").strip()

    if not user:
        raise BusinessException(BusinessExceptionEnum.InvalidUserEmail)
    if not case:
        raise BusinessException(BusinessExceptionEnum.InvalidCaseId)

    # CSV might have whitespace—strip and convert to int
    try:
        case_id = int(case)
    except (ValueError, TypeError):
        raise BusinessException(BusinessExceptionEnum.InvalidCaseId)

    return user, case_id


def validate_and_convert_top(row: Dict[str, str]) -> float or None:
    path = row.get(H_PATH, "").strip()
    top = row.get(H_TOP, "").strip()

    if not is_empty(top):
        # “Top” can’t be set on a root‐level path
        if len(path.split(".")) < 2:
            raise BusinessException(BusinessExceptionEnum.ConfigFileIncorrect)
        # The top config only allow number as input.
        try:
            return float(top)
        except (ValueError, TypeError):
            raise BusinessException(BusinessExceptionEnum.ConfigFileIncorrect)
    return None


def build_style_dict(
    collapse: str, highlight: str, top_value: float or None
) -> Dict[str, bool or float]:
    """
    Build a style‐dictionary from CSV columns:
      - Collapse: "TRUE" or "FALSE"
      - Highlight: "TRUE" or "FALSE"
      - Top: a float or empty

    If both Collapse and Highlight are empty‐strings and Top is None,
    returns {}.  Otherwise returns a dict with those keys present.
    """
    style: Dict[str, bool or float] = {}
    collapse_str = collapse.strip()
    highlight_str = highlight.strip()

    if not is_empty(collapse_str):
        style["collapse"] = str_to_bool(collapse_str)
    if not is_empty(highlight_str):
        style["highlight"] = str_to_bool(highlight_str)
    if top_value is not None:
        style["top"] = top_value

    return style


class CsvConfigurationParser:
    """
    Parses a CSV of the form:
       User,Case No.,Path,Collapse,Highlight,Top
       alice@example.com,12,BACKGROUND.Family History.Diabetes: Yes,TRUE,FALSE,
       alice@example.com,12,BACKGROUND.Medical History.Asthma: No,FALSE,TRUE,
       ...

    Our goal: For each distinct (user, case_id), collect *all* rows that share that pair,
    and produce exactly one DisplayConfig(user_email, case_id, path_config=[…]) object,
    where path_config is a list of {"path": PATH, "style": {...}} dictionaries.
    """

    def __init__(self, csv_stream: StringIO):
        reader = csv.DictReader(csv_stream, delimiter=",")
        self.rows: List[Dict[str, str]] = []
        for row in reader:
            self.rows.append(row)

    def parse(self) -> List[DisplayConfig]:
        # Step 1: bucket all rows by (user, case_id)
        # Map[(user, case_id)] → List[ (path_string, style_dict) ]
        buckets: Dict[Tuple[str, int], List[Dict[str, object]]] = {}

        for row in self.rows:
            # 1a) Extract user & case_id (or throw on invalid)
            user, case_id = validate_and_extract_user_case(row)

            # 1b) Determine “top” if any
            top_value = validate_and_convert_top(row)

            # 1c) Build style dictionary from Collapse/Highlight/Top
            collapse_str = row.get(H_COLLAPSE, "").strip()
            highlight_str = row.get(H_HIGHLIGHT, "").strip()
            style = build_style_dict(collapse_str, highlight_str, top_value)

            # 1d) The “Path” column must always exist (or we skip if empty)
            path = row.get(H_PATH, "").strip()
            if is_empty(path):
                # No path means nothing to do
                continue

            # Prepare a single entry: { "path": path, "style": style }.
            # If style is empty‐dict, we still include path—but style:{} is fine.
            entry: Dict[str, object] = {"path": path}
            if style:
                entry["style"] = style

            key = (user, case_id)
            if key not in buckets:
                buckets[key] = []
            buckets[key].append(entry)

        # Step 2: For each bucket, create a DisplayConfig
        result: List[DisplayConfig] = []
        for (user, case_id), entries in buckets.items():
            dc = DisplayConfig(user_email=user, case_id=case_id, path_config=[])
            dc.path_config = entries[:]  # copy list of {path, style} dicts
            result.append(dc)

        return result


def parse_csv_stream_to_configurations(csv_stream: StringIO) -> List[DisplayConfig]:
    return CsvConfigurationParser(csv_stream).parse()


def is_csv_file(filename: str or None) -> bool:
    if filename is None:
        return False
    _, ext = os.path.splitext(filename)
    return ext.lower() == ".csv"
