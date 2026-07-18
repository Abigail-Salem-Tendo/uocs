import enum
from datetime import datetime
from extensions import db


class ReportStatus(enum.Enum):
    REPORTED = "reported"
    VERIFIED = "verified"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"


class OutageReport(db.Model):
    """
    Core FR2 entity. A citizen-submitted outage report.

    Status is a real enum (not a free string) so invalid states are
    impossible at the DB layer — NFR12 relies on status being trustworthy
    (only Provider/Admin can transition it).

    Composite index on (location_id, utility_type_id, reported_at) —
    this is the exact lookup HotspotService will run: "3+ reports, same
    area, same utility type, within a 12hr window."
    """
    __tablename__ = "outage_reports"
    __table_args__ = (
        db.Index("ix_hotspot_lookup", "location_id", "utility_type_id", "reported_at"),
    )

    id = db.Column(db.Integer, primary_key=True)

    citizen_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey("locations.id"), nullable=False)
    utility_type_id = db.Column(db.Integer, db.ForeignKey("utility_types.id"), nullable=False)

    description = db.Column(db.Text, nullable=False)
    status = db.Column(
        db.Enum(ReportStatus),
        nullable=False,
        default=ReportStatus.REPORTED,
    )

    reported_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Relationships
    citizen = db.relationship("Citizen", backref="reports")
    location = db.relationship("Location", back_populates="reports")
    utility_type = db.relationship("UtilityType", back_populates="reports")

    def __repr__(self):
        return f"<OutageReport {self.id} {self.status.value}>"