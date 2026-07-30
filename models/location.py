from extensions import db


class Location(db.Model):
    """
    Represents the area an outage report is tied to.
    area_name is still what HotspotService groups reports by — that
    doesn't change. latitude/longitude are added as nullable columns
    so existing rows aren't affected; they're populated going forward
    via browser geolocation on report submission for map display.
    """
    __tablename__ = "locations"

    id = db.Column(db.Integer, primary_key=True)
    area_name = db.Column(db.String(100), nullable=False, index=True)
    address = db.Column(db.String(255), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)

    # Relationships
    reports = db.relationship("OutageReport", back_populates="location")

    def __repr__(self):
        return f"<Location {self.area_name}>"
    