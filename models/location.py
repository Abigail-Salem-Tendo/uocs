from extensions import db


class Location(db.Model):
    """
    Represents the area an outage report is tied to.
    For version one area/district name is what HotspotService groups
    reports by. No lat/long — nothing in the SRS requires map coordinates,
    and it can be added later as a non-breaking column addition.
    """
    __tablename__ = "locations"

    id = db.Column(db.Integer, primary_key=True)
    area_name = db.Column(db.String(100), nullable=False, index=True)
    address = db.Column(db.String(255), nullable=True)

    # Relationships
    reports = db.relationship("OutageReport", back_populates="location")

    def __repr__(self):
        return f"<Location {self.area_name}>"