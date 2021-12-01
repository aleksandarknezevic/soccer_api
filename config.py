import os
from pathlib import Path
from datetime import timedelta


dir_path = Path(os.path.dirname(os.path.realpath(__file__)))
path = dir_path
MOCK_URI = 'sqlite+pysqlite:///{file_path}'
FILE_PATH = f'{path}/db.sqlite3'
DB_URI = MOCK_URI.format(file_path=FILE_PATH)
DEBUG = True


class Config(object):
    OPENAPI_VERSION = '3.0.2'
    OPENAPI_JSON_PATH = 'api-spec.json'
    OPENAPI_URL_PREFIX = '/'
    OPENAPI_SWAGGER_UI_PATH = '/swagger-ui'
    OPENAPI_SWAGGER_UI_URL = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist/'
    OPENAPI_REDOC_PATH = '/redoc'
    OPENAPI_REDOC_URL = \
        'https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js'
    SQLALCHEMY_DATABASE_URI = DB_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = DEBUG
    JWT_TOKEN_LOCATION = ('headers', 'cookies')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=60)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=1)
    JWT_IDENTITY_CLAIM = 'sub'
    JWT_BLACKLIST_ENABLED = True
    JSON_SORT_KEYS = False


class Setting:
    def __init__(self):
        self.API_TITLE = os.environ.get('API_TITLE', 'SOCCER API')
        self.API_VERSION = os.environ.get('API_VERSION', '1.0')
        self.JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY',
                                             'pitmgpwezbidmhierprmfeode')
        self.DEFAULT_USER_EMAIL = 'example@toptal.com'
        self.DEFAULT_USER_NAME = 'godfather'
        self.DEFAULT_USER_PASSWORD = 'admin123.'


setting = Setting()
