from src import db


class SystemConfig(db.Model):
    __tablename__ = "system_config"

    id: int = db.Column(db.String(15), primary_key=True)
    json_config = db.Column(db.JSON, nullable=True)
