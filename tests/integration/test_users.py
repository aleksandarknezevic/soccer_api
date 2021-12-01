from app.main.factory import setting
from tests import admin_user, REGISTER_URL, \
    LOGIN_URL, USERS_URL, get_headers, REFRESH_URL

users = [
    {
        'name': 'admin2',
        'email': 'admin2@gmail.com',
        'password': 'sadfdrefsdrgfv',
        'role': 'admin'
    },
    {
        'name': 'user2',
        'email': 'user2@gmail.com',
        'password': 'wjrfjcedkw',
        'role': 'user'
    },
    {
        'name': 'user3',
        'email': 'user3@gmail.com',
        'password': 'wjrfjcedkw',
        'role': 'user'
    }
]


class TestUsers:
    user_ids = []

    def test_insert_users(self, test_client):
        headers = get_headers(test_client, admin_user)
        for user in users:
            ret = test_client.post(REGISTER_URL, json=user,
                                   headers=headers)
            self.user_ids.append(ret.json['id'])
            assert ret.status_code == 201

    def test_get_users_as_admin(self, test_client):
        headers = get_headers(test_client, admin_user)
        ret = test_client.get(USERS_URL, headers=headers)
        assert len(ret.json) > 1

    def test_get_users_as_user(self, test_client):
        headers = get_headers(test_client, users[1])
        ret = test_client.get(USERS_URL, headers=headers)
        assert len(ret.json) == 1
        assert ret.json[0]['name'] == users[1]['name']
        assert ret.json[0]['email'] == users[1]['email']

    def test_get_users_by_id_as_admin(self, test_client):
        headers = get_headers(test_client, admin_user)
        for i in range(len(users)):
            ret = test_client.get(USERS_URL + '/' + str(self.user_ids[i]),
                                  headers=headers)
            assert ret.status_code == 200
            assert ret.json['name'] == users[i]['name']
            assert ret.json['email'] == users[i]['email']
        ret = test_client.get(USERS_URL + '/' + str(10**9),
                              headers=headers)
        assert ret.status_code == 404

    def test_get_users_by_id_as_user(self, test_client):
        headers = get_headers(test_client, users[1])
        for i in range(len(users)):
            ret = test_client.get(USERS_URL + '/' + str(self.user_ids[i]),
                                  headers=headers)
            if i == 1:
                assert ret.status_code == 200
                assert ret.json['name'] == users[1]['name']
                assert ret.json['email'] == users[1]['email']
            else:
                assert ret.status_code == 403
        ret = test_client.delete(USERS_URL + '/' + str(10**9),
                                 headers=headers)
        assert ret.status_code == 403

    def test_delete_another_as_user(self, test_client):
        headers = get_headers(test_client, users[1])
        ret = test_client.delete(USERS_URL+'/' + str(self.user_ids[2]),
                                 headers=headers)
        assert ret.status_code == 403
        ret = test_client.delete(USERS_URL + '/' + str(10**9),
                                 headers=headers)
        assert ret.status_code == 403

    def test_delete_another_as_admin(self, test_client):
        headers = get_headers(test_client, admin_user)
        ret = test_client.delete(USERS_URL + '/' + str(10**9),
                                 headers=headers)
        assert ret.status_code == 404

    def test_delete_user_itself(self, test_client):
        tokens = test_client.post(LOGIN_URL, json=users[2])
        access_token = tokens.json['access_token']
        refresh_token = tokens.json['refresh_token']
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + access_token
        }
        ret = test_client.delete(USERS_URL + '/' + str(self.user_ids[2]),
                                 headers=headers)
        assert ret.status_code == 200
        assert not ret.json['active']
        # Test login again
        ret = test_client.post(LOGIN_URL, json=users[2])
        assert ret.status_code == 401
        # Test refreshing token deleted user
        headers['Authorization'] = 'Bearer ' + refresh_token
        ret = test_client.post(REFRESH_URL, headers=headers)
        assert ret.status_code == 401

    def test_patch_as_admin(self, test_client):
        headers = get_headers(test_client, admin_user)
        valid_user_patch = \
            {
                'email': 'admin1@gmail1.com',
                'role': 'admin',
                'name': 'Aleksandar Fleming'
            }
        ret = test_client.patch(USERS_URL + '/' + str(self.user_ids[1]),
                                json=valid_user_patch, headers=headers)
        assert ret.status_code == 200
        assert ret.json['email'] == valid_user_patch['email']
        assert ret.json['role'] == valid_user_patch['role']
        assert ret.json['name'] == valid_user_patch['name']

        valid_admin_patch = {
            'email': 'admin12@gmail1.com',
            'role': 'user',
            'name': 'Nikola Tesla'
        }
        ret = test_client.patch(USERS_URL + '/' + str(self.user_ids[0]),
                                json=valid_admin_patch, headers=headers)
        assert ret.status_code == 200
        assert ret.json['email'] == valid_admin_patch['email']
        assert ret.json['role'] == valid_admin_patch['role']
        assert ret.json['name'] == valid_admin_patch['name']

        invalid_email_patch = {'email': setting.DEFAULT_USER_EMAIL}
        ret = test_client.patch(USERS_URL + '/' + str(self.user_ids[0]),
                                json=invalid_email_patch, headers=headers)
        assert ret.status_code == 409
        ret = test_client.patch(USERS_URL + '/' + str(self.user_ids[1]),
                                json=invalid_email_patch, headers=headers)
        assert ret.status_code == 409

        # get data back
        for i in range(len(users)):
            ret = test_client.patch(USERS_URL + '/' + str(self.user_ids[i]),
                                    json=users[i], headers=headers)
            assert ret.status_code == 200

        # Test patching nonexistant user
        ret = test_client.patch(USERS_URL + '/' + str(10 ** 9),
                                json={'name': 'testname'}, headers=headers)
        assert ret.status_code == 404

    def test_patch_as_user(self, test_client):
        headers = get_headers(test_client, users[1])
        valid_patch = {
            'name': 'Alfred Hitchcock',
            'email': 'user123@gmail.com'
        }
        ret = test_client.patch(USERS_URL + '/' + str(self.user_ids[1]),
                                json=valid_patch, headers=headers)
        assert ret.status_code == 200
        assert ret.json['email'] == valid_patch['email']
        assert ret.json['name'] == valid_patch['name']
        # get data back
        back = users[1]
        back.pop('role')
        ret = test_client.patch(USERS_URL + '/' + str(self.user_ids[1]),
                                json=users[1], headers=headers)
        assert ret.status_code == 200
        assert ret.json['email'] == back['email']
        assert ret.json['name'] == back['name']

        invalid_patch = {'role': 'admin'}
        ret = test_client.patch(USERS_URL + '/' + str(self.user_ids[1]),
                                json=invalid_patch, headers=headers)
        assert ret.status_code == 403

        invalid_patch = {'active': False}
        ret = test_client.patch(USERS_URL + '/' + str(self.user_ids[1]),
                                json=invalid_patch, headers=headers)
        assert ret.status_code == 403

        # Test patching another user
        ret = test_client.patch(USERS_URL + '/' + str(self.user_ids[2]),
                                json=valid_patch, headers=headers)
        assert ret.status_code == 403

        # Test patching nonexistant user
        ret = test_client.patch(USERS_URL + '/' + str(10**9),
                                json={'team_id': 6}, headers=headers)
        assert ret.status_code == 403

    def test_reactivate_user(self, test_client):
        headers = get_headers(test_client, admin_user)
        data = {'active': True}
        ret = test_client.patch(USERS_URL+'/' + str(self.user_ids[2]),
                                headers=headers, json=data)
        assert ret.status_code == 200
        assert ret.json['email'] == users[2]['email'] and ret.json['active']
        ret = test_client.patch(USERS_URL + '/' + str(10**9),
                                headers=headers, json=data)
        assert ret.status_code == 404
