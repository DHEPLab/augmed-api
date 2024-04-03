from src import db


class Episode(db.Model):
    __tablename__ = "episode"

    episode_id = db.Column(db.Integer, primary_key=True, nullable=False)
    person_id = db.Column(db.Integer, db.ForeignKey("person.person_id"), nullable=False)
    episode_concept_id = db.Column(
        db.Integer, db.ForeignKey("concept.concept_id"), nullable=False
    )
    episode_start_date = db.Column(db.Date, nullable=False)
    episode_start_datetime = db.Column(db.TIMESTAMP)
    episode_end_date = db.Column(db.Date)
    episode_end_datetime = db.Column(db.TIMESTAMP)
    episode_parent_id = db.Column(db.Integer, db.ForeignKey("episode.episode_id"))
    episode_number = db.Column(db.Integer)
    episode_object_concept_id = db.Column(
        db.Integer, db.ForeignKey("concept.concept_id"), nullable=False
    )
    episode_type_concept_id = db.Column(
        db.Integer, db.ForeignKey("concept.concept_id"), nullable=False
    )
    episode_source_value = db.Column(db.String(50))
    episode_source_concept_id = db.Column(
        db.Integer, db.ForeignKey("concept.concept_id")
    )

    # Relationships
    person = db.relationship("Person", backref=db.backref("episodes", lazy="dynamic"))
    episode_concept = db.relationship(
        "Concept", foreign_keys=[episode_concept_id], backref="episodes_by_concept"
    )
    episode_object_concept = db.relationship(
        "Concept",
        foreign_keys=[episode_object_concept_id],
        backref="episodes_by_object",
    )
    episode_type_concept = db.relationship(
        "Concept", foreign_keys=[episode_type_concept_id], backref="episodes_by_type"
    )
    parent_episode = db.relationship(
        "Episode", remote_side=[episode_id], backref="child_episodes"
    )


# Note: Adjust relationship backref names as needed to avoid conflicts.
