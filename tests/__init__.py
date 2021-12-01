from config import setting

LOGIN_URL = '/auth/login'
REFRESH_URL = '/auth/refresh'
LOGOUT_URL = '/auth/logout'
REGISTER_URL = '/auth/register'
USERS_URL = '/users'
TEAMS_URL = '/teams'
PLAYERS_URL = '/players'
TRANSFERS_URL = '/transfers'

admin_user = {
    'email': setting.DEFAULT_USER_EMAIL,
    'password': setting.DEFAULT_USER_PASSWORD
}


def get_headers(test_client, user):
    headers = {
        'Content-Type': 'application/json',
    }
    email = user['email']
    password = user['password']
    ret = test_client.post(LOGIN_URL,
                           json={'email': email, 'password': password})
    headers['Authorization'] = 'Bearer ' + ret.json['access_token']
    return headers
