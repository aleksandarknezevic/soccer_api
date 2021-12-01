from typing import Any, Dict
from .crud_base import CRUDBase
from app.models import Team, PositionEnum, Player, db
from app.main.utils import get_random_persons
from random import randint


class CRUDTeam(CRUDBase[Team]):
    @staticmethod
    def generate_team(obj_in: Dict[str, Any]) -> Team:
        new_team = Team(
            country=obj_in['country'],
            name=obj_in['name']
        )
        number_of_players = 0
        for position in PositionEnum:
            number_of_players += int(position.value[1])
        persons = get_random_persons(number_of_players)
        cur = 0
        players = []
        for player_position in PositionEnum:
            for i in range(player_position.value[1]):
                person = persons[cur]
                player = Player(
                    first_name=person['first_name'],
                    last_name=person['last_name'],
                    country=person['country'],
                    position=player_position,
                    age=randint(18, 40)
                )
                players.append(player)
                cur += 1
        new_team.players = players
        return new_team

    def get_owner_id(self, team_id):
        team = self.get(team_id)
        return team.user_id

    def get_number_of_players(self, team_id):
        team = self.get(team_id)
        num = 0
        for player in list(team.players):
            if not player.transfer:
                num += 1
        return num

    @staticmethod
    def update_team_value(team_id):
        team = crud_team.get(team_id)
        val = 0
        for player in team.players:
            val += player.market_value
        team.team_value = val
        db.session.add(team)
        db.session.commit()
        db.session.refresh(team)

    @staticmethod
    def get_team_budget(team_id):
        return crud_team.get(team_id).budget

    @staticmethod
    def update_budget(team_id, amount):
        team = crud_team.get(team_id)
        team.budget += amount
        db.session.add(team)
        db.session.commit()
        db.session.refresh(team)


crud_team = CRUDTeam(Team)
