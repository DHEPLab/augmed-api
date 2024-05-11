from typing import List


class Diagnosis:
    def __init__(self, diagnosis, rationale, confidence):
        self.diagnosis = diagnosis
        self.rationale = rationale
        self.confidence = confidence

    diagnosis: str
    rationale: str
    confidence: int


class DiagnoseFormData:
    def __init__(self, diagnose, other):
        self.diagnose = diagnose
        self.other = other

    diagnose: List[Diagnosis]
    other: str
