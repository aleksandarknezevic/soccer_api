from .crud_base import db, CRUDBase
from .crud_team import crud_team
from app.models import Player
from random import randint


class CRUDPlayer(CRUDBase[Player]):
    def get_team_id(self, player_id):
        player = self.get(player_id)
        return player.team_id

    @staticmethod
    def transfer(player, team_id):
        old_team_id = player.team_id
        player.team_id = team_id
        increment_percent = randint(10, 100)
        player.market_value += (player.market_value * increment_percent)//100
        db.session.add(player)
        db.session.commit()
        db.session.refresh(player)
        if old_team_id:
            crud_team.update_team_value(old_team_id)
        crud_team.update_team_value(team_id)


crud_player = CRUDPlayer(Player)
