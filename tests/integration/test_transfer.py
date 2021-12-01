from .test_player import new_players, users
from tests import get_headers, admin_user, \
    REGISTER_URL, PLAYERS_URL, TEAMS_URL, TRANSFERS_URL
from app.crud import crud_team, crud_player


class TestTransfer:
    team_ids = []
    all_transfers = []

    def test_insert_players_users(self, test_client):
        headers = get_headers(test_client, admin_user)
        for user in users:
            ret = test_client.post(REGISTER_URL, json=user, headers=headers)
            assert ret.status_code == 201

    def test_get_team_ids(self, test_client):
        headers = get_headers(test_client, admin_user)
        teams = test_client.get(TEAMS_URL, headers=headers)
        for team in teams.json:
            self.team_ids.append(team['id'])
        assert len(self.team_ids) > 0

    def test_post_main(self, test_client):
        # as admin
        # create player with no team
        headers = get_headers(test_client, admin_user)
        admin_headers = headers
        new_player = test_client.post(
            PLAYERS_URL, json=new_players[0],
            headers=headers)
        new_player2 = test_client.post(
            PLAYERS_URL, json=new_players[0],
            headers=headers)
        assert new_player.status_code == 201
        transf = {
            'player_id': new_player.json['id'],
        }
        invalid_transfer = test_client.post(
            TRANSFERS_URL, json=transf,
            headers=headers)
        assert invalid_transfer.status_code == 422
        transf['price'] = 2000001
        valid_transfer = test_client.post(
            TRANSFERS_URL, json=transf,
            headers=headers)
        assert valid_transfer.status_code == 201
        assert valid_transfer.json['player']['id'] == new_player.json['id']
        assert valid_transfer.json['price'] == 2000001
        # Put player from team 3 on transfer list
        new_player = test_client.get(
            PLAYERS_URL + '?team_id=3',
            headers=headers)
        assert new_player.status_code == 200
        assert len(new_player.json) > 0
        player_id = new_player.json[0]['id']
        transf = {
            'player_id': player_id,
            'price': 2500000
        }
        valid_transfer = test_client.post(
            TRANSFERS_URL, json=transf,
            headers=headers)
        assert valid_transfer.status_code == 201
        assert valid_transfer.json['price'] == 2500000
        assert valid_transfer.json['player']['id'] == player_id
        # Test again same player
        invalid_transfer = test_client.post(
            TRANSFERS_URL, json=transf,
            headers=headers)
        assert invalid_transfer.status_code == 409
        # Nonexistant player
        transf['player_id'] = 10**9
        invalid_transfer = test_client.post(
            TRANSFERS_URL, json=transf,
            headers=headers)
        assert invalid_transfer.status_code == 404

        # as user
        headers = get_headers(test_client, users[0])
        my_players = test_client.get(PLAYERS_URL +
                                     '?team_id=' + str(self.team_ids[1]),
                                     headers=headers).json
        base_price = 3000000
        for i in range(9):
            transf = {
                'player_id': my_players[i]['id'],
                'price': base_price + i
            }
            valid_transfer = test_client.post(
                TRANSFERS_URL, json=transf,
                headers=headers)
            assert valid_transfer.status_code == 201
            assert valid_transfer.json['player']['id'] == my_players[i]['id']
            assert valid_transfer.json['price'] == base_price + i
        # Test 10th player
        transf = {
            'player_id': my_players[12]['id'],
            'price': base_price
        }
        invalid_transfer = test_client.post(
            TRANSFERS_URL, json=transf,
            headers=headers)
        print(transf)
        assert invalid_transfer.status_code == 403
        assert invalid_transfer.json['message'] ==\
               'Team has only 11 available players'
        # Test nonexistant player
        transf['player_id'] = 10 ** 9
        invalid_transfer = test_client.post(
            TRANSFERS_URL, json=transf,
            headers=headers)
        assert invalid_transfer.status_code == 403
        # Test not owned player
        admin_players = test_client.get(PLAYERS_URL +
                                        '?team_id=' + str(self.team_ids[0]),
                                        headers=admin_headers).json
        transf = {
            'player_id': admin_players[13]['id'],
            'price': base_price
        }
        invalid_transfer = test_client.post(
            TRANSFERS_URL, json=transf,
            headers=headers)
        assert invalid_transfer.status_code == 403
        # Test player with no team
        transf = {
            'player_id': new_player2.json['id'],
            'price': base_price
        }
        invalid_transfer = test_client.post(
            TRANSFERS_URL, json=transf,
            headers=headers)
        assert invalid_transfer.status_code == 403

    def test_get(self, test_client):
        # Unfiltered
        # as admin
        headers = get_headers(test_client, admin_user)
        admin_headers = headers
        all_transfers = test_client.get(TRANSFERS_URL, headers=headers)
        assert all_transfers.status_code == 200
        assert len(all_transfers.json) > 0
        for transfer in all_transfers.json:
            self.all_transfers.append(transfer)

        # as user
        all_transfers_user = test_client.get(TRANSFERS_URL, headers=headers)
        assert all_transfers_user.status_code == 200
        assert len(all_transfers_user.json) > 0
        assert all_transfers_user.json == all_transfers.json

        # Filters
        # test invalid combinations
        invalid_queries = [
            '?value_gt=100&value=102',
            '?value_gt=100&value_lt=100',
            '?value_lt=1000&value=100',
            '?price_gt=100&price_lt=88',
            '?price=10000&price_lt=100000022',
            '?price=10000&price_gt=100000022'
        ]
        for query in invalid_queries:
            invalid_filtered = test_client.get(
                TRANSFERS_URL + query,
                headers=admin_headers)
            assert invalid_filtered.status_code == 422
        team_id = int(self.all_transfers[-1]
                      ['player']['links']['team'].split('/')[-1])
        team_name = crud_team.get(team_id).name
        filter_team = '?team_name=' + team_name
        filtered_by_team = test_client.get(
            TRANSFERS_URL+filter_team,
            headers=admin_headers)
        assert filtered_by_team.status_code == 200
        assert len(filtered_by_team.json) == 9
        filter_name = '?first_name=' + new_players[0]['first_name'] + \
                      '&last_name=' + new_players[0]['last_name']
        filtered_by_name = test_client.get(
            TRANSFERS_URL+filter_name,
            headers=admin_headers)

        assert filtered_by_name.status_code == 200
        assert len(filtered_by_name.json) == 1

        country = self.all_transfers[-1]['player']['country']
        filter_country = '?country=' + country
        filtered_by_country = test_client.get(
            TRANSFERS_URL+filter_country,
            headers=admin_headers)
        assert filtered_by_country.status_code == 200
        expected_number = len([tr for tr in self.all_transfers
                               if tr['player']['country'] == country])
        assert len(filtered_by_country.json) == expected_number

        values = [transfer['player']['market_value'] for transfer
                  in self.all_transfers]
        prices = [transfer['price'] for transfer in self.all_transfers]
        min_value = min(values)
        max_value = max(values)
        min_price = min(prices)
        max_price = max(prices)
        if min_value < max_value:
            filter_value = '?value_gt=' + \
                           str(min_value-1) + '&value_lt=' + str(max_value)
            filtered_by_value = test_client.get(
                TRANSFERS_URL + filter_value,
                headers=admin_headers)
            assert filtered_by_value.status_code == 200
            assert len(filtered_by_value.json) == \
                   len([val for val in values if max_value >
                        val > min_value - 1])
        filter_value = '?value=' + str(min_value)
        filtered_by_value = test_client.get(
            TRANSFERS_URL + filter_value,
            headers=admin_headers)
        assert filtered_by_value.status_code == 200
        assert len(filtered_by_value.json) == \
               len([val for val in values if val == min_value])

        if min_price < max_price:
            filter_price = '?price_gt=' + \
                           str(min_price - 1) + \
                           '&price_lt=' + str(max_price)
            filtered_by_price = test_client.get(
                TRANSFERS_URL + filter_price,
                headers=admin_headers)
            assert filtered_by_price.status_code == 200
            assert len(filtered_by_price.json) == \
                   len([price for price in prices if (min_price - 1)
                        < price < max_price])
        filter_price = '?price=' + str(min_price)
        filtered_by_price = test_client.get(
            TRANSFERS_URL + filter_price,
            headers=admin_headers)
        assert filtered_by_price.status_code == 200
        assert len(filtered_by_price.json) == \
               len([price for price in prices if price == min_price])

    def test_get_by_id(self, test_client):
        admin_headers = get_headers(test_client, admin_user)
        for transfer in self.all_transfers:
            transfer_get = test_client.get(
                TRANSFERS_URL + '/' + str(transfer['id']),
                headers=admin_headers)
            assert transfer_get.status_code == 200
            assert transfer_get.json['id'] == transfer['id']
        # Test nonexistant
        transfer_get = test_client.get(
            TRANSFERS_URL + '/' + str(10**9),
            headers=admin_headers)
        assert transfer_get.status_code == 404

        # as user
        user_headers = get_headers(test_client, users[0])
        for transfer in self.all_transfers:
            transfer_get = test_client.get(
                TRANSFERS_URL + '/' + str(transfer['id']),
                headers=user_headers)
            assert transfer_get.status_code == 200
            assert transfer_get.json['id'] == transfer['id']
        # Test nonexistant
        transfer_get = test_client.get(
            TRANSFERS_URL + '/' + str(10 ** 9),
            headers=user_headers)
        assert transfer_get.status_code == 404

    def test_delete(self, test_client):
        # as admin
        admin_headers = get_headers(test_client, admin_user)
        transfer_id = str(10**9)
        delete_transfer = test_client.delete(
            TRANSFERS_URL + '/' + transfer_id,
            headers=admin_headers)
        assert delete_transfer.status_code == 404
        # test existing transfer
        transfer_id = str(self.all_transfers[2]['id'])
        del self.all_transfers[2]
        delete_transfer = test_client.delete(
            TRANSFERS_URL + '/' + transfer_id,
            headers=admin_headers)
        assert delete_transfer.status_code == 204

        # as user
        user_headers = get_headers(test_client, users[0])
        transfer_id = str(10 ** 9)
        delete_transfer = test_client.delete(
            TRANSFERS_URL + '/' +
            transfer_id,
            headers=user_headers)
        assert delete_transfer.status_code == 403
        # Test another transfer
        for transfer in self.all_transfers:
            if transfer['player']['links']['team'] == '/teams/3':
                another_transfer_id = str(transfer['id'])
                break
        if another_transfer_id:
            delete_transfer = test_client.delete(
                TRANSFERS_URL + '/' +
                another_transfer_id,
                headers=user_headers)
            assert delete_transfer.status_code == 403
        # Test another transfer
        for i in range(len(self.all_transfers)):
            if self.all_transfers[i]['player']['links']['team'] == '/teams/2':
                my_transfer_id = str(self.all_transfers[i]['id'])
                del self.all_transfers[i]
                break
        if my_transfer_id:
            delete_transfer = test_client.delete(
                TRANSFERS_URL + '/' + my_transfer_id,
                headers=user_headers)
            assert delete_transfer.status_code == 204

    def test_patch(self, test_client):
        admin_headers = get_headers(test_client, admin_user)
        user_header = get_headers(test_client, users[0])
        for headers in [admin_headers, user_header]:
            for transfer in self.all_transfers:
                old_price = transfer['price']
                patch = {
                    'price': 3000000
                }
                revert_patch = {
                    'price': old_price
                }
                patch_transfer = test_client.patch(
                    TRANSFERS_URL + '/' + str(transfer['id']),
                    json=patch,
                    headers=headers)
                if headers == admin_headers:
                    assert patch_transfer.status_code == 200
                    assert patch_transfer.json['price'] == 3000000
                    revert_patch_transfer = test_client.patch(
                        TRANSFERS_URL + '/' +
                        str(transfer['id']),
                        json=revert_patch,
                        headers=headers)
                    assert revert_patch_transfer.status_code == 200
                else:
                    if transfer['player']['links']['team'] == '/teams/2':
                        assert patch_transfer.status_code == 200
                        assert patch_transfer.json['price'] == 3000000
                        revert_patch_transfer = test_client.patch(
                            TRANSFERS_URL + '/' +
                            str(transfer['id']),
                            json=revert_patch,
                            headers=headers)
                        assert revert_patch_transfer.status_code == 200
                    else:
                        assert patch_transfer.status_code == 403
            invalid_patch = test_client.patch(TRANSFERS_URL + '/' + str(10**9),
                                              json={'price': 3000000},
                                              headers=headers)
            assert invalid_patch.status_code == 404

    def test_buy(self, test_client):
        user_headers = get_headers(test_client, users[0])
        admin_headers = get_headers(test_client, admin_user)
        # Test nonexistant transfer
        transfer = test_client.put(TRANSFERS_URL + '/' +
                                   str(10**9),
                                   headers=user_headers)
        assert transfer.status_code == 404
        # Test buying self player
        tested_own = False
        tested_no_team = False
        tested_third_team = False
        tested_no_budget = False
        for transfer in self.all_transfers:
            if tested_own and tested_no_budget and\
                    tested_no_team and tested_third_team:
                break
            if transfer['player']['links']['team'] == \
                    '/teams/2' and not tested_own:
                transfer_put = test_client.put(TRANSFERS_URL +
                                               '/' + str(transfer['id']),
                                               headers=user_headers)
                assert transfer_put.status_code == 409
                tested_own = True
            if transfer['player']['links']['team'] != \
                    '/teams/2' and not tested_no_budget:
                team2_budget = crud_team.get_team_budget(2)
                old_price = transfer['price']
                patch = {
                    'price': team2_budget + 1
                }
                tr_patch = test_client.patch(TRANSFERS_URL + '/' +
                                             str(transfer['id']),
                                             json=patch,
                                             headers=admin_headers)
                assert tr_patch.status_code == 200
                transfer_put = test_client.put(TRANSFERS_URL + '/' +
                                               str(transfer['id']),
                                               headers=user_headers)
                assert transfer_put.status_code == 409
                transfer_get = test_client.get(TRANSFERS_URL + '/' +
                                               str(transfer['id']),
                                               headers=user_headers)
                assert transfer_get.status_code == 200
                patch = {
                    'price': old_price
                }
                tr_patch = test_client.patch(TRANSFERS_URL + '/' +
                                             str(transfer['id']),
                                             json=patch,
                                             headers=admin_headers)
                assert tr_patch.status_code == 200
                tested_no_budget = True
            if transfer['player']['links']['team'] == \
                    '/teams/3' and not tested_third_team:
                old_player_value = transfer['player']['market_value']
                player_id = transfer['player']['id']
                price = transfer['price']
                transfer_id = transfer['id']
                old_team2_budget = crud_team.get_team_budget(2)
                old_team3_budget = crud_team.get_team_budget(3)
                old_team2_value = crud_team.get(2).team_value
                old_team3_value = crud_team.get(3).team_value
                old_team2_players = len(list(crud_team.get(2).players))
                old_team3_players = len(list(crud_team.get(3).players))
                transfer_put = test_client.put(TRANSFERS_URL + '/' +
                                               str(transfer_id),
                                               headers=user_headers)
                assert transfer_put.status_code == 200
                transfer_get = test_client.get(TRANSFERS_URL + '/' +
                                               str(transfer_id),
                                               headers=user_headers)
                assert transfer_get.status_code == 404
                assert crud_team.get_team_budget(2) == old_team2_budget - price
                assert crud_team.get_team_budget(3) == old_team3_budget + price
                new_player_value = crud_player.get(player_id).market_value
                assert old_player_value // 10 - 1 < new_player_value <\
                       2 * old_player_value + 1
                assert len(list(crud_team.get(2).players)) == \
                       old_team2_players + 1
                assert len(list(crud_team.get(3).players)) == \
                       old_team3_players - 1
                assert old_team3_value == crud_team.get(3).team_value + \
                       old_player_value
                assert old_team2_value == crud_team.get(2).team_value -\
                       new_player_value
                tested_third_team = True
            if transfer['player']['links']['team'] is None and\
                    not tested_no_team:
                old_player_value = transfer['player']['market_value']
                player_id = transfer['player']['id']
                price = transfer['price']
                transfer_id = transfer['id']
                old_team2_budget = crud_team.get_team_budget(2)
                old_team2_value = crud_team.get(2).team_value
                old_team2_players = len(list(crud_team.get(2).players))
                transfer_put = test_client.put(TRANSFERS_URL + '/' +
                                               str(transfer_id),
                                               headers=user_headers)
                assert transfer_put.status_code == 200
                transfer_get = test_client.get(TRANSFERS_URL + '/' +
                                               str(transfer_id),
                                               headers=user_headers)
                assert transfer_get.status_code == 404
                assert crud_team.get_team_budget(2) == old_team2_budget - price
                new_player_value = crud_player.get(player_id).market_value
                assert old_player_value // 10 - 1 < new_player_value \
                       < 2 * old_player_value + 1
                assert len(list(crud_team.get(2).players)) == \
                       old_team2_players + 1
                assert old_team2_value == crud_team.get(2).team_value \
                       - new_player_value
                tested_no_team = True
