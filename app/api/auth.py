from flask_smorest import Blueprint, abort
from flask_jwt_extended import (
    get_jwt_identity,
    get_jwt,
    create_access_token,
    create_refresh_token,
    jwt_required
)
from flask.views import MethodView
from app.schemas import (UserRegisterSchema, UserGetSchema,
                         UserLoginSchema, TokenSchema)
from app.crud import crud_token, crud_user


auth_blp = Blueprint('Auth',
                     __name__,
                     url_prefix='/auth',
                     description='Authentication Operations')


@auth_blp.route('/register')
class UserRegister(MethodView):
    @auth_blp.arguments(schema=UserRegisterSchema)
    @auth_blp.response(schema=UserGetSchema, status_code=201)
    @jwt_required(optional=True)
    def post(self, new_user):
        if crud_user.get_by_email(new_user['email']):
            abort(
                409,
                message='A user with this email already exists in the system')
        requester_is_admin = crud_user.is_admin(
            crud_user.get(get_jwt_identity()))
        if 'role' in new_user and new_user['role'] == 'admin' \
                and not requester_is_admin:
            new_user['role'] = 'user'
        user = crud_user.create(new_user)
        return user


@auth_blp.route('/login')
class UserLogin(MethodView):
    @auth_blp.arguments(UserLoginSchema)
    @auth_blp.response(200, TokenSchema)
    def post(self, new_data):

        user = crud_user.authenticate(email=new_data['email'],
                                      password=new_data['password'])
        if not user:
            abort(401, message='Wrong email address or password')
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        response_data = {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer'
        }
        return response_data


@auth_blp.route('/refresh')
class RefreshToken(MethodView):
    @jwt_required(refresh=True)
    @auth_blp.response(200, TokenSchema)
    def post(self):
        current_user_id = get_jwt_identity()
        access_token = create_access_token(identity=current_user_id)
        response_data = {
            'access_token': access_token,
            'token_type': 'Bearer'
        }
        return response_data


@auth_blp.route('/logout')
class UserLogoutAccess(MethodView):
    @jwt_required()
    def post(self):
        jti = get_jwt()['jti']
        crud_token.revoke(jti)
        return {'message': 'Logged out'}
