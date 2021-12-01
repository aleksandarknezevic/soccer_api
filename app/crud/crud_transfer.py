from .crud_base import CRUDBase
from app.models import Transfer, Player, Team, db


class CRUDTransfer(CRUDBase[Transfer]):
    def create(self, price: int, player: Player) -> Transfer:
        new_transfer = Transfer()
        new_transfer.price = price
        new_transfer.player = player
        db.session.add(new_transfer)
        db.session.commit()
        db.session.refresh(new_transfer)
        return new_transfer

    def filtered_search(self, data):
        query = db.session.query(Transfer).join(Player)
        if 'team_name' in data:
            query = query.join(Team).filter(Team.name == data['team_name'])
        if 'country' in data:
            query = query.filter(Player.country == data['country'])
        if 'first_name' in data:
            query = query.filter(Player.first_name == data['first_name'])
        if 'last_name' in data:
            query = query.filter(Player.last_name == data['last_name'])
        if 'price' in data:
            query = query.filter(self.model.price == data['price'])
        if 'price_lt' in data:
            query = query.filter(self.model.price < data['price_lt'])
        if 'price_gt' in data:
            query = query.filter(self.model.price > data['price_gt'])
        if 'value' in data:
            query = query.filter(Player.market_value == data['value'])
        if 'value_gt' in data:
            query = query.filter(Player.market_value > data['value_gt'])
        if 'value_lt' in data:
            query = query.filter(Player.market_value < data['value_lt'])

        result = query.all()
        return result


crud_transfer = CRUDTransfer(Transfer)
