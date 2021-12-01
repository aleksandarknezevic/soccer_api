import requests

base_url = 'https://randomuser.me/api'
query = '&gender=male&inc=gender,nat,name,location'


def get_random_persons(count=1):
    full_query = '/?results=' + str(count) + query
    try:
        response = requests.get(base_url + full_query)
        persons = response.json()
        person_list = []
        for person in persons['results']:
            person_list.append({
                'first_name': person['name']['first'],
                'last_name': person['name']['last'],
                'country': person['location']['country']
            })
    except Exception:
        person_list = count * [{
            'first_name': 'John',
            'last_name': 'Wick',
            'country': 'United States of America'
        }]
    return person_list


def get_random_country():
    try:
        response = requests.get(base_url + '/?results=1' + query)
        country = response.json()['results'][0]['location']['country']
    except Exception:
        country = 'Serbia'
    return country
