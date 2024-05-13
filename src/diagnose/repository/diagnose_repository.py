from src.diagnose.model.diagnose import Diagnose


class DiagnoseRepository:
    def __init__(self, session):
        self.session = session

    def add_diagonose(self, diagnose: Diagnose):
        self.session.add(diagnose)
        self.session.flush()
        return diagnose
