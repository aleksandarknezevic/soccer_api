from tests import admin_user, get_headers, TEAMS_URL, REGISTER_URL
from random import choice
from . import generate_random_string

users = [
    {
        'name': 'teams_user1',
        'email': 'teams-user1@toptal.com',
        'password': 'ejejrvlnkdddefv'
    }
]


class TestTeams:

    team_ids = []

    def test_insert_teams_users(self, test_client):
        headers = get_headers(test_client, admin_user)
        for user in users:
            ret = test_client.post(REGISTER_URL, json=user, headers=headers)
            assert ret.status_code == 201

    def test_teams(self, test_client):
        headers = get_headers(test_client, users[0])
        ret = test_client.get(TEAMS_URL, headers=headers)
        assert ret.status_code == 200
        assert len(ret.json) == 1

        headers = get_headers(test_client, admin_user)
        ret = test_client.get(TEAMS_URL, headers=headers)
        assert ret.status_code == 200
        assert len(ret.json) > 0

    def test_get_teams_by_id(self, test_client):
        headers = get_headers(test_client, users[0])
        ret = test_client.get(TEAMS_URL, headers=headers)
        user1_team_id = ret.json[0]['id']
        user1_team_name = ret.json[0]['name']
        assert ret.status_code == 200
        assert len(ret.json) == 1

        headers = get_headers(test_client, admin_user)
        ret = test_client.get(TEAMS_URL, headers=headers)
        for team in ret.json:
            self.team_ids.append(team['id'])
        ret = test_client.get(
            TEAMS_URL + '/' + str(user1_team_id),
            headers=headers)
        assert ret.status_code == 200
        assert ret.json['name'] == user1_team_name
        ret = test_client.get(
            TEAMS_URL + '/' + str(10**9),
            headers=headers)
        assert ret.status_code == 404

        # As user
        headers = get_headers(test_client, users[0])
        for team_id in self.team_ids:
            ret = test_client.get(
                TEAMS_URL + '/' + str(team_id),
                headers=headers)
            if team_id != user1_team_id:
                assert ret.status_code == 403
            else:
                assert ret.status_code == 200
                assert ret.json['name'] == user1_team_name
        ret = test_client.get(
            TEAMS_URL + '/' + str(10**9),
            headers=headers)
        assert ret.status_code == 403

    def test_patch(self, test_client):
        # As admin
        headers = get_headers(test_client, admin_user)
        for team_id in self.team_ids:
            ret = test_client.patch(
                TEAMS_URL + '/' + str(team_id),
                json={'name': generate_random_string(choice([2, 256]))},
                headers=headers)
            assert ret.status_code == 422
            name = generate_random_string(15)
            ret = test_client.patch(
                TEAMS_URL + '/' + str(team_id),
                json={'name': name},
                headers=headers)
            assert ret.status_code == 200
            assert ret.json['name'] == name
            ret = test_client.patch(
                TEAMS_URL + '/' + str(team_id),
                json={'country': 'Srbija'},
                headers=headers)
            assert ret.status_code == 200
            assert ret.json['country'] == 'Srbija'
            budget = 100000000
            ret = test_client.patch(
                TEAMS_URL + '/' + str(team_id),
                json={'budget': budget},
                headers=headers)
            assert ret.status_code == 200
            assert ret.json['budget'] == budget
            budget = -100000000
            ret = test_client.patch(TEAMS_URL + '/' + str(team_id),
                                    json={'budget': budget},
                                    headers=headers)
            assert ret.status_code == 422
        ret = test_client.patch(
            TEAMS_URL + '/' + str(10**9),
            json={'budget': 1000},
            headers=headers)
        assert ret.status_code == 404
        # As user
        headers = get_headers(test_client, users[0])
        ret = test_client.get(TEAMS_URL, headers=headers)
        user1_team_id = ret.json[0]['id']
        for team_id in self.team_ids:
            name = generate_random_string(15)
            ret = test_client.patch(TEAMS_URL + '/' + str(team_id),
                                    json={'name': name},
                                    headers=headers)
            if team_id == user1_team_id:
                assert ret.status_code == 200
                assert ret.json['name'] == name
            else:
                assert ret.status_code == 403
            ret = test_client.patch(TEAMS_URL + '/' + str(team_id),
                                    json={'country': 'Srbija'},
                                    headers=headers)
            if team_id == user1_team_id:
                assert ret.status_code == 200
                assert ret.json['country'] == 'Srbija'
            else:
                assert ret.status_code == 403
            budget = 100000000
            ret = test_client.patch(TEAMS_URL + '/' +
                                    str(team_id),
                                    json={'budget': budget},
                                    headers=headers)
            assert ret.status_code == 403
        ret = test_client.patch(
            TEAMS_URL + '/' + str(10**9),
            json={'budget': 1000},
            headers=headers)
        assert ret.status_code == 403
