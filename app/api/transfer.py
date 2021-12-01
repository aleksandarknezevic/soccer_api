from flask_smorest import Blueprint, abort
from flask.views import MethodView
from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required
)
from app.crud import crud_user, crud_player, crud_team, crud_transfer
from app.schemas import TransferGetSchema, TransferWriteSchema, \
    TransferPatchSchema, PlayerGetSchema, TransferFilterSchema
from .utils import CursorPage


transfer_blp = Blueprint('Transfers',
                         __name__,
                         url_prefix='/transfers',
                         description='Operations on Transfers')


@transfer_blp.route('')
class Transfers(MethodView):
    @transfer_blp.arguments(TransferFilterSchema, location='query')
    @transfer_blp.response(200, TransferGetSchema(many=True))
    @transfer_blp.paginate(CursorPage, max_page_size=300, page_size=30)
    @jwt_required()
    def get(self, filters):
        return crud_transfer.filtered_search(filters)

    @transfer_blp.arguments(TransferWriteSchema)
    @transfer_blp.response(201, TransferGetSchema())
    @jwt_required()
    def post(self, new_transfer):
        requester_user_id = get_jwt_identity()
        player_id = new_transfer['player_id']
        player = crud_player.get(player_id)
        is_admin = crud_user.is_admin(crud_user.get(requester_user_id))
        if not player:
            if not is_admin:
                abort(403)
            else:
                abort(404, message='Player does not exists')
        if player.transfer:
            abort(409, message='Player is already on transfer list')
        team_id = crud_player.get_team_id(player.id)
        if team_id:
            player_owner_id = crud_team.get_owner_id(team_id)
            if not is_admin and player_owner_id != requester_user_id:
                abort(403)
            else:
                if crud_team.get_number_of_players(team_id) > 11:
                    return crud_transfer.create(new_transfer['price'], player)
                else:
                    abort(403, message='Team has only 11 available players')
        else:
            if not is_admin:
                abort(403)
            else:
                return crud_transfer.create(new_transfer['price'], player)


@transfer_blp.route('<int:transfer_id>')
class TransferById(MethodView):
    @transfer_blp.response(200, TransferGetSchema)
    @jwt_required()
    def get(self, transfer_id):
        transfer = crud_transfer.get(transfer_id)
        if not transfer:
            abort(404)
        return transfer

    @transfer_blp.response(204)
    @jwt_required()
    def delete(self, transfer_id):
        transfer = crud_transfer.get(transfer_id)
        requester_user_id = get_jwt_identity()
        is_admin = crud_user.is_admin(crud_user.get(requester_user_id))
        if not transfer:
            if not is_admin:
                abort(403)
            abort(404)
        owner_id = crud_team.get_owner_id(
            crud_player.get_team_id(transfer.player_id))
        if not is_admin:
            if owner_id != requester_user_id:
                abort(403)
        crud_transfer.delete(transfer_id)
        return

    @transfer_blp.arguments(TransferPatchSchema)
    @transfer_blp.response(200, TransferGetSchema)
    @jwt_required()
    def patch(self, new_data, transfer_id):
        transfer = crud_transfer.get(transfer_id)
        if not transfer:
            abort(404)
        requester_user_id = get_jwt_identity()
        is_admin = crud_user.is_admin(crud_user.get(requester_user_id))
        team_id = crud_player.get_team_id(transfer.player_id)
        if not team_id:
            if not is_admin:
                abort(403)
        else:
            owner_id = crud_team.get_owner_id(team_id)
        if not is_admin:
            if owner_id != requester_user_id:
                abort(403)
        return crud_transfer.update(transfer, new_data)

    @transfer_blp.response(200, PlayerGetSchema)
    @jwt_required()
    def put(self, transfer_id):
        transfer = crud_transfer.get(transfer_id)
        if not transfer:
            abort(404)
        requester_user_id = get_jwt_identity()
        request_team_id = crud_user.get(requester_user_id).team.id
        owner_id = transfer.player.team_id
        if request_team_id == owner_id:
            abort(409, message='You can\'t buy your player')
        if crud_team.get_team_budget(request_team_id) >= transfer.price:
            crud_player.transfer(crud_player.get(transfer.player_id),
                                 request_team_id)
            if owner_id:
                crud_team.update_budget(owner_id, transfer.price)
            crud_team.update_budget(request_team_id, 0-transfer.price)
            crud_transfer.delete(transfer_id)
            return crud_player.get(transfer.player_id)
        else:
            abort(409, message='You don\'t have enough funds')
