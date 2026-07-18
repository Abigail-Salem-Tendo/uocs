"""
Central import point for all models.

Flask-Migrate/SQLAlchemy only knows a table exists once its model class
has been imported somewhere in the chain. Importing everything here — and
importing this package once in app.py — guarantees all models are
registered in db.metadata before any `flask db migrate` runs, regardless
of which model happens to reference which via ForeignKey.
"""

from models.user import User, Citizen, UtilityProvider, Admin
from models.location import Location
from models.utility_type import UtilityType
from models.outage_report import OutageReport, ReportStatus