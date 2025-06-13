from src.analytics.model.analytics import Analytics

class AnalyticsRepository:
    def __init__(self, session):
        self.session = session

    def add(self, analytics: Analytics) -> Analytics:
        self.session.add(analytics)
        self.session.flush()
        return analytics
