from flask_smorest import Blueprint, abort
from flask.views import MethodView
from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required
)
from app.crud import crud_user, crud_player, crud_team, crud_transfer
from app.schemas import PlayerGetSchema, PlayerWriteSchema, PlayerFiltersSchema
from .utils import CursorPage


player_blp = Blueprint('Players',
                       __name__,
                       url_prefix='/players',
                       description='Operations on Players')


@player_blp.route('')
class Players(MethodView):
    @player_blp.arguments(PlayerFiltersSchema, location='query')
    @player_blp.response(200, PlayerGetSchema(many=True))
    @player_blp.paginate(CursorPage, max_page_size=300, page_size=30)
    @jwt_required()
    def get(self, filters):
        user_id = get_jwt_identity()
        user = crud_user.get(user_id)
        if filters:
            team_id = filters['team_id']
            if not crud_user.is_admin(user) and team_id != user.team.id:
                abort(403)
            team = crud_team.get(team_id)
            if not team:
                return []
            else:
                return list(team.players)
        else:
            if not crud_user.is_admin(user):
                team_id = user.team.id
                return list(crud_team.get(team_id).players)
            else:
                return crud_player.get_all()

    @player_blp.arguments(PlayerWriteSchema)
    @player_blp.response(201, PlayerGetSchema)
    @jwt_required()
    def post(self, new_player):
        request_user_id = get_jwt_identity()
        if not crud_user.is_admin(crud_user.get(request_user_id)):
            abort(403)
        player = crud_player.create(new_player)
        if 'team_id' in new_player:
            crud_team.update_team_value(new_player['team_id'])
        return player


@player_blp.route('<int:player_id>')
class PlayerById(MethodView):
    @player_blp.response(200, PlayerGetSchema())
    @jwt_required()
    def get(self, player_id):
        request_user_id = get_jwt_identity()
        user = crud_user.get(request_user_id)
        requester_team_id = user.team.id
        player = crud_player.get(player_id)
        if not player:
            if not crud_user.is_admin(user):
                abort(403)
            abort(404)
        if not crud_user.is_admin(user) \
                and requester_team_id != player.team_id:
            abort(403)
        return player

    @player_blp.response(204)
    @jwt_required()
    def delete(self, player_id):
        request_user_id = get_jwt_identity()
        user = crud_user.get(request_user_id)
        if not crud_user.is_admin(user):
            abort(403)
        player = crud_player.get(player_id)
        if not player:
            abort(404)
        team_id = crud_player.get_team_id(player_id)
        if team_id and crud_team.get_number_of_players(team_id) <= 11:
            abort(409, message='Team has minimum number '
                               'of players, can\'t be deleted')
        crud_player.delete(player_id)
        if team_id:
            crud_team.update_team_value(team_id)

    @player_blp.arguments(PlayerWriteSchema)
    @player_blp.response(200, PlayerGetSchema)
    @jwt_required()
    def patch(self, new_data, player_id):
        request_user_id = get_jwt_identity()
        player = crud_player.get(player_id)
        if not player:
            if not crud_user.is_admin(crud_user.get(request_user_id)):
                abort(403)
            abort(404)
        teams = set()
        team_id = crud_player.get_team_id(player_id)
        owner_id = None
        if team_id:
            teams.add(team_id)
            owner_id = crud_team.get_owner_id(team_id)
        if not crud_user.is_admin(crud_user.get(request_user_id)):
            if len(teams) == 0 or owner_id != request_user_id:
                abort(403)
            for param in ['market_value', 'age', 'position', 'team_id']:
                if param in new_data:
                    abort(403, message='You are not '
                                       'allowed to change value for ' + param)
            updated_player = crud_player.update(player, new_data)
        else:
            update_team_value = False
            if 'team_id' in new_data:
                if not crud_team.get(new_data['team_id']):
                    abort(422, message='New team not found')
                teams.add(new_data['team_id'])
                update_team_value = True
            if 'market_value' in new_data:
                update_team_value = True
            updated_player = crud_player.update(player, new_data)
            if update_team_value:
                for t in teams:
                    crud_team.update_team_value(t)
        return updated_player
