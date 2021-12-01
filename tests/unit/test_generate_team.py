from app.crud import crud_team
from tests.integration import generate_random_string
from app.main.utils import get_random_country


def test_generate_team():
    country = get_random_country()
    name = generate_random_string(20)
    obj_in = {
        'name': name,
        'country': country
    }
    team = crud_team.generate_team(obj_in)
    assert team.name == name
    assert team.country == country
    assert len(list(team.players)) == 20
