from tests import admin_user, get_headers, TEAMS_URL, REGISTER_URL, PLAYERS_URL
from app.crud import crud_team

users = [
    {
        'name': 'teams_user1',
        'email': 'teams-user1@toptal.com',
        'password': 'ejejrvlnkdddefv'
    },
    {
        'name': 'teams_admin1',
        'email': 'teams-admin1@toptal.com',
        'password': 'SJDHEELNCKSSdefcs'
    }
]

new_players = [
    {
        'first_name': 'Linus',
        'last_name': 'Torvalds',
        'position': 'defender',
        'market_value': 3000200,
        'country': 'Finland',
        'age': 28
    },
    {
        'first_name': 'Richard',
        'last_name': 'Stollman',
        'position': 'goalkeeper',
        'market_value': 3000200,
        'country': 'USA'
    }
]


class TestPlayers:
    team_ids = []

    def test_insert_players_users(self, test_client):
        headers = get_headers(test_client, admin_user)
        for user in users:
            ret = test_client.post(REGISTER_URL, json=user, headers=headers)
            assert ret.status_code == 201

    def test_unfiltered_get(self, test_client):
        # as admin
        headers = get_headers(test_client, admin_user)
        teams = test_client.get(TEAMS_URL, headers=headers)
        for team in teams.json:
            self.team_ids.append(team['id'])
        players = test_client.get(
            PLAYERS_URL + '?page_size=100', headers=headers)
        assert players.status_code == 200
        number_of_players = 0
        for team in self.team_ids:
            number_of_players += crud_team.get_number_of_players(team)
        assert number_of_players == len(players.json) == 60

        # as user
        headers = get_headers(test_client, users[0])
        players = test_client.get(
            PLAYERS_URL + '?page_size=100', headers=headers)
        assert players.status_code == 200
        assert len(players.json) == 20

    def test_filtered_get(self, test_client):
        # as admin
        headers = get_headers(test_client, admin_user)
        for team_id in self.team_ids:
            players = test_client.get(
                PLAYERS_URL + '?page_size=100&&team_id=' +
                str(team_id), headers=headers)
            assert players.status_code == 200
            assert len(players.json) == 20
        # test nonexistent team_id
        players = test_client.get(
            PLAYERS_URL + '?page_size=100&&team_id=' +
            str(10 ** 9), headers=headers)
        assert players.status_code == 200
        assert len(players.json) == 0
        # test invalid team_id
        players = test_client.get(
            PLAYERS_URL + '?page_size=100&&team_id=-50',
            headers=headers)
        assert players.status_code == 422

        # as user
        headers = get_headers(test_client, users[0])
        self_team_id = test_client.get(
            TEAMS_URL, headers=headers).json[0]['id']
        for team_id in self.team_ids:
            players = test_client.get(
                PLAYERS_URL + '?page_size=100&&team_id=' +
                str(team_id), headers=headers)
            if team_id == self_team_id:
                assert players.status_code == 200
                assert len(players.json) == 20
            else:
                assert players.status_code == 403
        # test nonexistent team_id
        players = test_client.get(
            PLAYERS_URL + '?page_size=100&&team_id=' +
            str(10 ** 9), headers=headers)
        assert players.status_code == 403

    def test_post(self, test_client):
        # as user
        headers = get_headers(test_client, users[0])
        user_team_id = test_client.get(
            TEAMS_URL, headers=headers).json[0]['id']
        new_player = test_client.post(
            PLAYERS_URL, json=new_players[0],
            headers=headers)
        assert new_player.status_code == 403
        my_player = new_players[1]
        my_player['team_id'] = user_team_id
        my_new_player = test_client.post(
            PLAYERS_URL, json=new_players[0],
            headers=headers)
        assert my_new_player.status_code == 403

        # as admin
        headers = get_headers(test_client, admin_user)
        user_team_value = crud_team.get(user_team_id).team_value
        user_team_budget = crud_team.get_team_budget(user_team_id)
        new_player_no_team = test_client.post(
            PLAYERS_URL, json=new_players[0],
            headers=headers)
        assert new_player_no_team.status_code == 201
        assert new_player_no_team.json['first_name'] == \
               new_players[0]['first_name']
        assert new_player_no_team.json['last_name'] ==\
               new_players[0]['last_name']
        assert new_player_no_team.json['country'] ==\
               new_players[0]['country']
        assert new_player_no_team.json['position'] ==\
               new_players[0]['position']
        assert new_player_no_team.json['age'] == new_players[0]['age']
        assert new_player_no_team.json['links']['team'] is None

        team_new_player = new_players[1]
        team_new_player['team_id'] = user_team_id
        new_player_team = test_client.post(
            PLAYERS_URL, json=team_new_player,
            headers=headers)
        assert new_player_team.status_code == 201
        assert new_player_team.json['links']['team'] == \
               '/teams/' + str(user_team_id)
        assert crud_team.get_team_budget(user_team_id) == user_team_budget
        assert user_team_value + new_player_team.json['market_value'] ==\
               crud_team.get(user_team_id).team_value

    def test_get_by_id(self, test_client):
        headers = get_headers(test_client, admin_user)
        player_ids = []
        for team_id in self.team_ids:
            team_players = test_client.get(
                PLAYERS_URL + '?page_size=100&&team_id=' +
                str(team_id), headers=headers)
            player_ids.append([team_players.json[0]['id'], team_id])
        # As admin
        for player_id in player_ids:
            player = test_client.get(
                PLAYERS_URL + '/' + str(player_id[0]),
                headers=headers)
            assert player.status_code == 200
            assert player.json['id'] == player_id[0]
        # test nonexistent
        player = test_client.get(
            PLAYERS_URL + '/' + str(10 ** 9),
            headers=headers)
        assert player.status_code == 404

        # as user
        headers = get_headers(test_client, users[0])
        user_team_id = test_client.get(
            TEAMS_URL, headers=headers).json[0]['id']
        for player_id in player_ids:
            player = test_client.get(
                PLAYERS_URL + '/' + str(player_id[0]),
                headers=headers)
            if player_id[1] == user_team_id:
                assert player.status_code == 200
                assert player.json['id'] == player_id[0]
            else:
                assert player.status_code == 403
        # test nonexistent
        player = test_client.get(
            PLAYERS_URL + '/' + str(10 ** 9),
            headers=headers)
        assert player.status_code == 403

    def test_delete(self, test_client):
        # as admin
        headers = get_headers(test_client, admin_user)
        admin_headers = headers
        all_teams = test_client.get(
            TEAMS_URL,
            headers=headers).json
        # test no team
        new_player_no_team = new_players[0]
        new_player = test_client.post(
            PLAYERS_URL, json=new_player_no_team,
            headers=headers)
        new_player_id = new_player.json['id']
        assert all_teams == test_client.get(
            TEAMS_URL,
            headers=headers).json
        deleted_player = test_client.delete(
            PLAYERS_URL + '/' + str(new_player_id),
            headers=headers)
        assert deleted_player.status_code == 204
        get_player = test_client.get(
            PLAYERS_URL + '/' +
            str(new_player_id), headers=headers)
        assert get_player.status_code == 404
        # Delete players from last team
        players = test_client.get(
            PLAYERS_URL + '?page_size=100&&team_id=' +
            str(self.team_ids[-1]), headers=headers)
        while len(players.json) > 11:
            player = players.json[0]
            value = player['market_value']
            team_value = test_client.get(
                TEAMS_URL + '/' + str(self.team_ids[-1]),
                headers=headers).json['team_value']
            delete_player = test_client.delete(
                PLAYERS_URL + '/' + str(player['id']),
                headers=headers)
            assert delete_player.status_code == 204
            assert team_value == test_client.get(
                TEAMS_URL + '/' + str(self.team_ids[-1]), headers=headers
            ).json['team_value'] + value
            players = test_client.get(
                PLAYERS_URL + '?page_size=100&&team_id='
                + str(self.team_ids[-1]),
                headers=headers)
        # test deleting 11th player
        players = test_client.get(
            PLAYERS_URL + '?page_size=100&&team_id=' + str(self.team_ids[-1]),
            headers=headers)
        player_id = players.json[0]['id']
        delete_player = test_client.delete(
            PLAYERS_URL + '/' + str(player_id),
            headers=headers)
        assert delete_player.status_code == 409
        # test deleting nonexistant player
        delete_player = test_client.delete(
            PLAYERS_URL + '/' + str(10 ** 9),
            headers=headers)
        assert delete_player.status_code == 404

        # as user
        headers = get_headers(test_client, users[0])
        user_team_id = test_client.get(
            TEAMS_URL, headers=headers).json[0]['id']
        # Delete players from user team
        players = test_client.get(
            PLAYERS_URL + '?page_size=100&&team_id=' + str(user_team_id),
            headers=headers)
        player_id = players.json[0]['id']
        delete_player = test_client.delete(
            PLAYERS_URL + '/' + str(player_id), headers=headers)
        assert delete_player.status_code == 403

        # Test deleting another's team player
        admin_team_id = test_client.get(TEAMS_URL,
                                        headers=admin_headers).json[0]['id']
        player_id = test_client.get(
            PLAYERS_URL + '?page_size=100&&team_id=' + str(admin_team_id),
            headers=admin_headers).json[0][
            'id']
        delete_player = test_client.delete(
            PLAYERS_URL + '/' + str(player_id),
            headers=headers)
        assert delete_player.status_code == 403

        # Test deleting nonexistant player
        delete_player = test_client.delete(
            PLAYERS_URL + '/' + str(10 ** 9),
            headers=headers)
        assert delete_player.status_code == 403

    def test_patch(self, test_client):
        # as admin
        headers = get_headers(test_client, admin_user)
        # test switching player from team[1] to team[2] changing all values
        player = test_client.get(
            PLAYERS_URL + '?page_size=100&&team_id=' + str(self.team_ids[1]),
            headers=headers).json[0]
        team1_value = test_client.get(
            TEAMS_URL + '/' + str(self.team_ids[1]),
            headers=headers).json['team_value']
        team2_value = test_client.get(
            TEAMS_URL + '/' + str(self.team_ids[2]), headers=headers
        ).json['team_value']
        player_initial_value = player['market_value']
        player['first_name'] = new_players[0]['first_name']
        player['last_name'] = new_players[0]['last_name']
        player['country'] = new_players[0]['country']
        player['market_value'] = new_players[0]['market_value']
        player['position'] = new_players[0]['position']
        player['team_id'] = self.team_ids[-1]
        player_id = player['id']
        changed_player = test_client.patch(
            PLAYERS_URL + '/' + str(player_id),
            json=player, headers=headers)
        assert changed_player.status_code == 200
        assert changed_player.json['market_value'] == player['market_value']
        assert changed_player.json['first_name'] == player['first_name']
        assert changed_player.json['last_name'] == player['last_name']
        assert changed_player.json['position'] == player['position']
        assert team1_value == test_client.get(
            TEAMS_URL + '/' + str(self.team_ids[1]),
            headers=headers
        ).json['team_value'] + player_initial_value
        assert team2_value == test_client.get(
            TEAMS_URL + '/' + str(self.team_ids[2]),
            headers=headers
        ).json['team_value'] - new_players[0]['market_value']
        # test nonexistant player
        changed_player = test_client.patch(
            PLAYERS_URL + '/' + str(10 ** 9),
            json=player, headers=headers)
        assert changed_player.status_code == 404
        # test moving to nonexistant team
        patch = {'team_id': 10 ** 9}
        changed_player = test_client.patch(
            PLAYERS_URL + '/' + str(player_id),
            json=patch, headers=headers)
        print(changed_player.json)
        assert changed_player.status_code == 422
        assert changed_player.json['message'] == 'New team not found'

        # as user
        headers = get_headers(test_client, users[0])
        user_patch = {
            'first_name': 'Aleksandar',
            'last_name': 'Knezevic',
            'country': 'Serbia'
        }
        # Another player
        changed_player = test_client.patch(
            PLAYERS_URL + '/' + str(player_id),
            json=user_patch,
            headers=headers)
        assert changed_player.status_code == 403
        # own player
        user_team_id = test_client.get(
            TEAMS_URL, headers=headers).json[0]['id']
        players = test_client.get(
            PLAYERS_URL + '?page_size=100&&team_id=' + str(user_team_id),
            headers=headers)
        my_player_id = players.json[0]['id']
        changed_player = test_client.patch(
            PLAYERS_URL + '/' + str(my_player_id),
            json=user_patch,
            headers=headers)
        assert changed_player.status_code == 200
        assert changed_player.json['first_name'] == user_patch['first_name']
        assert changed_player.json['last_name'] == user_patch['last_name']
        assert changed_player.json['country'] == user_patch['country']
        # test forbidden fields
        patches = [{'market_value': 1}, {'position': 'defender'},
                   {'age': 22}, {'team_id': 1000}]
        for patch in patches:
            changed_player = test_client.patch(
                PLAYERS_URL + '/' + str(my_player_id),
                json=patch,
                headers=headers)
            print(changed_player.json)
            assert changed_player.status_code == 403

        # nonexistant player
        changed_player = test_client.patch(
            PLAYERS_URL + '/' + str(10 ** 9),
            json=user_patch,
            headers=headers)
        assert changed_player.status_code == 403
