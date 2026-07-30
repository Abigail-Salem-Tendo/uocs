from flask import Flask, redirect, url_for, flash
from flask_login import current_user, logout_user
from config import Config
from extensions import db, bcrypt, login_manager, migrate, csrf
import models


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    @app.context_processor
    def inject_google_maps_key():
        import os
        return dict(google_maps_api_key=os.environ.get("GOOGLE_MAPS_API_KEY", ""))

    login_manager.login_view = 'auth.login'

    from models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.before_request
    def enforce_active_session():
        """
        Global guard: if Admin deactivates a user mid-session, this ends
        it on their very next request instead of waiting for them to log
        out themselves. @login_required alone only checks
        is_authenticated, not is_active, so this closes that gap.
        """
        if current_user.is_authenticated and not current_user.active:
            logout_user()
            flash('This account has been deactivated. Contact an administrator.', 'error')
            return redirect(url_for('auth.login'))

    from routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    from routes.citizen import citizen_bp
    app.register_blueprint(citizen_bp)

    from routes.provider import provider_bp
    app.register_blueprint(provider_bp)

    from routes.admin_routes import admin_bp
    app.register_blueprint(admin_bp)

    from routes.map_routes import map_bp
    app.register_blueprint(map_bp)

    from utils.seed import seed_db
    app.cli.add_command(seed_db)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
