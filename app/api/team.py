from flask_smorest import Blueprint, abort
from flask.views import MethodView
from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required
)
from app.crud import crud_user, crud_team
from app.schemas import TeamGetSchema, TeamPatchSchema
from .utils import CursorPage

team_blp = Blueprint('Teams',
                     __name__,
                     url_prefix='/teams',
                     description='Operations on Teams')


@team_blp.route("")
class Teams(MethodView):
    @team_blp.response(200, TeamGetSchema(many=True))
    @team_blp.paginate(CursorPage, max_page_size=300, page_size=30)
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = crud_user.get(user_id)
        if not crud_user.is_admin(user):
            return [user.team]
        return crud_team.get_all()


@team_blp.route('<int:team_id>')
class TeamById(MethodView):
    @team_blp.response(200, TeamGetSchema())
    @jwt_required()
    def get(self, team_id):
        request_user_id = get_jwt_identity()
        user = crud_user.get(request_user_id)
        requester_team_id = user.team.id
        if not crud_user.is_admin(user) and requester_team_id != team_id:
            abort(403)
        team = crud_team.get(team_id)
        if not team:
            abort(404)
        return team

    @team_blp.arguments(schema=TeamPatchSchema())
    @team_blp.response(200, TeamGetSchema())
    @jwt_required()
    def patch(self, request_data, team_id):
        request_user_id = get_jwt_identity()
        team = crud_team.get(team_id)
        admin = crud_user.is_admin(crud_user.get(request_user_id))
        if not team:
            if not admin:
                abort(403)
            abort(404)
        owner_id = crud_team.get_owner_id(team_id)

        if not admin:
            if request_user_id != owner_id or 'budget' in request_data:
                abort(403)
        team = crud_team.update(team, request_data)
        return team
