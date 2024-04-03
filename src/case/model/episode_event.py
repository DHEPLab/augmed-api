from src import db


class EpisodeEvent(db.Model):
    __tablename__ = "episode_event"

    episode_id = db.Column(
        db.Integer,
        db.ForeignKey("episode.episode_id"),
        primary_key=True,
        nullable=False,
    )
    event_id = db.Column(
        db.Integer, primary_key=True, nullable=False
    )  # Assuming event_id could refer to various types of events
    episode_event_field_concept_id = db.Column(
        db.Integer, db.ForeignKey("concept.concept_id"), nullable=False
    )

    # Relationships - Assuming an Episode and Concept model are defined elsewhere
    episode = db.relationship(
        "Episode", backref=db.backref("episode_events", lazy="dynamic")
    )
    episode_event_field_concept = db.relationship("Concept", backref="episode_events")
