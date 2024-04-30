from dataclasses import dataclass
from typing import List


@dataclass
class CaseSummary:
    config_id: int
    case_id: int
    patient_chief_complaint: str
    age: str
    gender: str


@dataclass
class GetCaseSummaryResponse:
    summaries: List[CaseSummary]
