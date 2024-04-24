from src.cases.model.clinical_data.person.person import Person


class PersonRepository:
    def __init__(self, session):
        self.session = session

    def get_person(self, person_id: int):
        return self.session.get(Person, person_id)
