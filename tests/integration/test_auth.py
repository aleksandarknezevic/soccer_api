from . import generate_random_string
from tests import LOGIN_URL, LOGOUT_URL, REFRESH_URL, REGISTER_URL
from app.main.factory import setting


DELETE_USER_URL = '/users/2'

users = [
    {
        'name': 'admin1',
        'email': 'admin1@gmail.com',
        'password': 'sadfdrefsdrgfv',
        'role': 'admin'
    },
    {
        'name': 'admin2',
        'email': 'admin2@gmail.com',
        'password': 'wjrfjcedkw',
        'role': 'admin'
    }
]


class TestAuth:
    admin_jwt_token = None

    def test_login_wrong_password(self, test_client):
        email = setting.DEFAULT_USER_EMAIL
        password = generate_random_string(30)
        ret = test_client.post(LOGIN_URL, json={'email': email,
                                                'password': password})
        assert ret.status_code == 401

    def test_login_wrong_email(self, test_client):
        email = generate_random_string(12)+'@'+generate_random_string(5)+'.com'
        password = generate_random_string(30)
        ret = test_client.post(LOGIN_URL,
                               json={'email': email,
                                     'password': password})
        assert ret.status_code == 401

    def test_login_jwt(self, test_client):
        email = setting.DEFAULT_USER_EMAIL
        password = setting.DEFAULT_USER_PASSWORD
        ret = test_client.post(LOGIN_URL,
                               json={'email': email,
                                     'password': password})
        ret_val = ret.json
        assert ret.status_code == 200
        TestAuth.admin_jwt_token = ret_val.pop('access_token')
        TestAuth.admin_refresh_jwt_token = ret_val.pop('refresh_token')

    def test_registering_user_without_jwt(self, test_client):
        ret = test_client.post(REGISTER_URL, json=users[0])
        assert ret.status_code == 201
        assert ret.json['email'] == users[0]['email']
        assert ret.json['name'] == users[0]['name']
        assert ret.json['role'] == 'user'

    def test_login_as_new_user(self, test_client):
        ret = test_client.post(LOGIN_URL, json=users[0])
        assert ret.status_code == 200
        TestAuth.user0_jwt_token = ret.json.pop('access_token')
        TestAuth.user0_refresh_jwt_token = ret.json.pop('refresh_token')

    def test_register_existing_email(self, test_client):
        user = users[0]
        user['password'] = generate_random_string(12)
        ret = test_client.post(REGISTER_URL, json=user)
        assert ret.status_code == 409

    def test_register_admin(self, test_client):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + TestAuth.admin_jwt_token
        }
        ret = test_client.post(REGISTER_URL, json=users[1], headers=headers)
        assert ret.status_code == 201
        assert ret.json['role'] == 'admin'

    def test_deactivate_user(self, test_client):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + TestAuth.admin_jwt_token
        }
        ret = test_client.delete(DELETE_USER_URL, headers=headers)
        assert ret.status_code == 200
        assert not ret.json['active']

    def test_login_as_inactive(self, test_client):
        ret = test_client.post(LOGIN_URL, json=users[0])
        assert ret.status_code == 401

    def test_refresh_token_admin(self, test_client):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + TestAuth.admin_refresh_jwt_token
        }
        ret = test_client.post(REFRESH_URL, headers=headers)
        assert ret.status_code == 200
        TestAuth.admin_jwt_token = ret.json.pop('access_token')

    def test_refresh_token_inactive(self, test_client):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + TestAuth.user0_refresh_jwt_token
        }
        ret = test_client.post(REFRESH_URL, headers=headers)
        assert ret.status_code == 401

    def test_logout_admin(self, test_client):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + TestAuth.admin_jwt_token
        }
        ret = test_client.post(LOGOUT_URL, headers=headers)
        assert ret.status_code == 200
        assert ret.json['message'] == 'Logged out'

    def test_logout_inactive(self, test_client):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + TestAuth.user0_jwt_token
        }
        ret = test_client.post(LOGOUT_URL, headers=headers)
        assert ret.status_code == 401
