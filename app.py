from flask import Flask
from config import Config
from extensions import db, bcrypt, login_manager, migrate
import models


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = 'auth.login'

    from models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from routes.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    from routes.citizen import citizen_bp
    app.register_blueprint(citizen_bp)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
