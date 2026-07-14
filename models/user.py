from datetime import datetime
from flask_login import UserMixin
from extensions import db, bcrypt


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Discriminator column for Single Table Inheritance
    user_type = db.Column(db.String(20), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': user_type
    }

    def set_password(self, plain_password):
        self.password_hash = bcrypt.generate_password_hash(plain_password).decode('utf-8')

    def check_password(self, plain_password):
        return bcrypt.check_password_hash(self.password_hash, plain_password)

    def __repr__(self):
        return f'<User {self.email} ({self.user_type})>'


class Citizen(User):
    __mapper_args__ = {
        'polymorphic_identity': 'citizen'
    }


class UtilityProvider(User):
    # Nullable for now — will become a real FK once UtilityType model exists (Phase 2)
    utility_type_id = db.Column(db.Integer, nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': 'provider'
    }


class Admin(User):
    __mapper_args__ = {
        'polymorphic_identity': 'admin'
    }
