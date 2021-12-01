from flask_smorest import Blueprint, abort, response
from flask.views import MethodView
from flask_jwt_extended import (
    get_jwt_identity,
    get_jwt,
    jwt_required
)
from app.crud import crud_user, crud_token, crud_team
from app.schemas import UserGetSchema, UserPatchSchema
from .utils import CursorPage


user_blp = Blueprint('Users',
                     __name__,
                     url_prefix='/users',
                     description='Operations on Users')


@user_blp.route('')
class Users(MethodView):
    @user_blp.response(200, UserGetSchema(many=True))
    @user_blp.paginate(CursorPage, max_page_size=300, page_size=30)
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = crud_user.get(user_id)
        if not crud_user.is_admin(user):
            return [user]
        users = crud_user.get_all()
        return users


@user_blp.route('<int:user_id>')
class UserById(MethodView):
    @user_blp.response(200, UserGetSchema())
    @jwt_required()
    def get(self, user_id):
        request_user_id = get_jwt_identity()
        user = crud_user.get(request_user_id)
        if not crud_user.is_admin(user) and request_user_id != user_id:
            abort(403)
        user = crud_user.get(user_id)
        if not user:
            abort(404)
        return user

    @user_blp.response(200, UserGetSchema())
    @jwt_required()
    def delete(self, user_id):
        request_user_id = get_jwt_identity()
        user = crud_user.get(user_id)
        if not crud_user.is_admin(crud_user.get(request_user_id)) and \
                request_user_id != user_id:
            abort(403)
        if not user:
            abort(404)
        if crud_user.is_active(user):
            user = crud_user.delete(user_id)
            if user_id == request_user_id:
                crud_token.revoke(get_jwt()['jti'])
        return user

    @user_blp.arguments(schema=UserPatchSchema())
    @user_blp.response(200, UserGetSchema())
    @jwt_required()
    def patch(self, request_data, user_id):
        request_user_id = get_jwt_identity()
        user = crud_user.get(user_id)
        admin = crud_user.is_admin(crud_user.get(request_user_id))
        if not admin:
            if request_user_id != user_id or 'role' in request_data \
                    or 'active' in request_data:
                abort(403)
        if not user:
            abort(404)
        if 'email' in request_data and \
                crud_user.get_by_email(request_data['email']) and \
                crud_user.get_by_email(request_data['email']) != user:
            abort(409, message='Invalid email: User already exists')
        user = crud_user.update(user, request_data)
        return user
