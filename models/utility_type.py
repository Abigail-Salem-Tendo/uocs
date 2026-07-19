from extensions import db


class UtilityType(db.Model):
    """
    Represents a type of utility (Electricity, Water, etc).
    V1 scope is electricity-only, but this is a real table (not a hardcoded
    string) so new types can be added later with zero schema change —
    satisfies NFR10 and matches the Class Diagram.
    """
    __tablename__ = "utility_types"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    # Relationships
    reports = db.relationship("OutageReport", back_populates="utility_type")
    providers = db.relationship("UtilityProvider", back_populates="utility_type")

    def __repr__(self):
        return f"<UtilityType {self.name}>"