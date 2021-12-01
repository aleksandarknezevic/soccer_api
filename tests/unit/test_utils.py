from app.main.utils import get_random_country,\
    get_random_persons


def test_get_country():
    for _ in range(10):
        country = get_random_country()
        assert isinstance(country, str)
        assert 3 <= len(country) < 256


def test_get_persons():
    for _ in range(10):
        persons = get_random_persons(50)
        for person in persons:
            assert isinstance(person, dict)
            assert 'first_name' in person
            assert 'last_name' in person
            assert 'country' in person
