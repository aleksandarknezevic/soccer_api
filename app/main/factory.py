from flask import Flask
from config import Config, setting
from flask_jwt_extended import JWTManager, get_jwt
from flask_smorest import Api
from app.models import db
from app.schemas import ma
from app.crud import crud_token
from app.crud import crud_user


jwt = JWTManager()


@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(_, jwt_payload):
    jti = jwt_payload['jti']
    if not crud_user.is_active(crud_user.get(jwt_payload['sub'])):
        crud_token.revoke(jti)
    return crud_token.is_revoked(jti)


def create_app(db_path=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['API_TITLE'] = setting.API_TITLE
    app.config['API_VERSION'] = setting.API_VERSION
    app.config['JWT_SECRET_KEY'] = setting.JWT_SECRET_KEY
    if db_path:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite+pysqlite:///' + db_path
        app.config['TESTING'] = True
    api = Api(app)

    db.init_app(app)

    with app.app_context():
        db.create_all()
    app.db = db

    jwt.init_app(app)
    ma.init_app(app)

    from app.api import auth_blp, user_blp, team_blp, player_blp, transfer_blp
    api.register_blueprint(user_blp)
    api.register_blueprint(auth_blp)
    api.register_blueprint(team_blp)
    api.register_blueprint(player_blp)
    api.register_blueprint(transfer_blp)

    with app.app_context():
        if not crud_user.get_by_email(setting.DEFAULT_USER_EMAIL):
            default_user_data = {
                'name': setting.DEFAULT_USER_NAME,
                'password': setting.DEFAULT_USER_PASSWORD,
                'email': setting.DEFAULT_USER_EMAIL,
                'role': 'admin'
            }
            crud_user.create(default_user_data)

    return app
