## Introduction

Task is done in Python programming language and flask framework. For database in this project I used sqlite (by default db will be created in file `db.sqlite3` in the root of project. Besides Python and flask I used some python libraries and all of them are written in file requirements.txt in root of this project. The most important ones are:

* Flask-sqlalchemy - For ORM operations
* flask-smorest - for API resources, building documentation
* flask-marshmallow - for creating schemas for json objects for the interaction with the app and for input vaidation
* pytest - for the unit and integrations tests

## Project structure

 In the root directory you can find next:

* __app__ - directory with flask project
  * __app/api__ - directory with all of API resources
  * __app/crud__ - directory with crud classes
  * __app/main__ - directory where app factory stored, security functions and utils
  * __app/models__ - directory where all db models are stored
  * __app/schemas__ - directory where all marshmallow schema stored
* __docs__ - directory related to the project documentation
  * __docs/api-spec.json__ - JSON file with documented APIs (also visible on APP_URL/swagger-ui or APP_URL/redoc in prettier form)
* __infra__ - directory with files related to the infrastructure
  * __infra/docker-compose.yaml__ - config file for docker-compose for running the app
  * __infra/docker-compose.tests.yaml__ - docker-compose config file for running tests
  * __Dockerfile__ - dockerfile for creating docker image to run test and application
* __tests__ - directory where all tests are stored
  * __tests/integration__ - Directory where all integration tests are defined
  * __tests/unit__ - Directory where all unit tests are defined
* __.gitignore__ - thing which should be ignored from VCS
* __config.py__ - config file for the application
* __README.md__ - this file
* __requirements.txt__ - all python libs used in project
* __run.py__ - start point for the application

## Configuring application

When the application started it uses config parameters from file `config.py` (in the root of project). If you want to change default username, database file location, JWT secret token you should change it here. Note that some of these parameters for running tests are overridden in file `tests/conftest.py`. 

## Running application and/or test using docker-compose

### Required tools for running application

In order to run application you will need:

- [Docker](https://docs.docker.com/engine/install/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Building docker image

Before starting either application or tests it is good to build docker image if not built. You can do it by running:

`docker-compose -f infra/docker-compose.yaml build`

### Running tests

In order to run tests you should run command (from the root of project):

```bazaar
docker-compose -f infra/docker-compose.tests.yaml up \
    --abort-on-container-exit --exit-code-from app && \
    docker-compose -f infra/docker-compose.yaml rm -fsv
```

If everything is OK you will see output:

```
app    | ============================= test session starts ==============================
app    | platform linux -- Python 3.9.7, pytest-6.2.5, py-1.11.0, pluggy-1.0.0 -- /usr/local/bin/python
app    | cachedir: .pytest_cache
app    | rootdir: /app
app    | collecting ... collected 46 items
app    | 
app    | tests/integration/test_auth.py::TestAuth::test_login_wrong_password PASSED [  2%]
app    | tests/integration/test_auth.py::TestAuth::test_login_wrong_email PASSED  [  4%]
app    | tests/integration/test_auth.py::TestAuth::test_login_jwt PASSED          [  6%]
app    | tests/integration/test_auth.py::TestAuth::test_registering_user_without_jwt PASSED [  8%]
app    | tests/integration/test_auth.py::TestAuth::test_login_as_new_user PASSED  [ 10%]
app    | tests/integration/test_auth.py::TestAuth::test_register_existing_email PASSED [ 13%]
app    | tests/integration/test_auth.py::TestAuth::test_register_admin PASSED     [ 15%]
app    | tests/integration/test_auth.py::TestAuth::test_deactivate_user PASSED    [ 17%]
app    | tests/integration/test_auth.py::TestAuth::test_login_as_inactive PASSED  [ 19%]
app    | tests/integration/test_auth.py::TestAuth::test_refresh_token_admin PASSED [ 21%]
app    | tests/integration/test_auth.py::TestAuth::test_refresh_token_inactive PASSED [ 23%]
app    | tests/integration/test_auth.py::TestAuth::test_logout_admin PASSED       [ 26%]
app    | tests/integration/test_auth.py::TestAuth::test_logout_inactive PASSED    [ 28%]
app    | tests/integration/test_player.py::TestPlayers::test_insert_players_users PASSED [ 30%]
app    | tests/integration/test_player.py::TestPlayers::test_unfiltered_get PASSED [ 32%]
app    | tests/integration/test_player.py::TestPlayers::test_filtered_get PASSED  [ 34%]
app    | tests/integration/test_player.py::TestPlayers::test_post PASSED          [ 36%]
app    | tests/integration/test_player.py::TestPlayers::test_get_by_id PASSED     [ 39%]
app    | tests/integration/test_player.py::TestPlayers::test_delete PASSED        [ 41%]
app    | tests/integration/test_player.py::TestPlayers::test_patch PASSED         [ 43%]
app    | tests/integration/test_team.py::TestTeams::test_insert_teams_users PASSED [ 45%]
app    | tests/integration/test_team.py::TestTeams::test_teams PASSED             [ 47%]
app    | tests/integration/test_team.py::TestTeams::test_get_teams_by_id PASSED   [ 50%]
app    | tests/integration/test_team.py::TestTeams::test_patch PASSED             [ 52%]
app    | tests/integration/test_transfer.py::TestTransfer::test_insert_players_users PASSED [ 54%]
app    | tests/integration/test_transfer.py::TestTransfer::test_get_team_ids PASSED [ 56%]
app    | tests/integration/test_transfer.py::TestTransfer::test_post_main PASSED  [ 58%]
app    | tests/integration/test_transfer.py::TestTransfer::test_get PASSED        [ 60%]
app    | tests/integration/test_transfer.py::TestTransfer::test_get_by_id PASSED  [ 63%]
app    | tests/integration/test_transfer.py::TestTransfer::test_delete PASSED     [ 65%]
app    | tests/integration/test_transfer.py::TestTransfer::test_patch PASSED      [ 67%]
app    | tests/integration/test_transfer.py::TestTransfer::test_buy PASSED        [ 69%]
app    | tests/integration/test_users.py::TestUsers::test_insert_users PASSED     [ 71%]
app    | tests/integration/test_users.py::TestUsers::test_get_users_as_admin PASSED [ 73%]
app    | tests/integration/test_users.py::TestUsers::test_get_users_as_user PASSED [ 76%]
app    | tests/integration/test_users.py::TestUsers::test_get_users_by_id_as_admin PASSED [ 78%]
app    | tests/integration/test_users.py::TestUsers::test_get_users_by_id_as_user PASSED [ 80%]
app    | tests/integration/test_users.py::TestUsers::test_delete_another_as_user PASSED [ 82%]
app    | tests/integration/test_users.py::TestUsers::test_delete_another_as_admin PASSED [ 84%]
app    | tests/integration/test_users.py::TestUsers::test_delete_user_itself PASSED [ 86%]
app    | tests/integration/test_users.py::TestUsers::test_patch_as_admin PASSED   [ 89%]
app    | tests/integration/test_users.py::TestUsers::test_patch_as_user PASSED    [ 91%]
app    | tests/integration/test_users.py::TestUsers::test_reactivate_user PASSED  [ 93%]
app    | tests/unit/test_generate_team.py::test_generate_team PASSED              [ 95%]
app    | tests/unit/test_utils.py::test_get_country PASSED                        [ 97%]
app    | tests/unit/test_utils.py::test_get_persons PASSED                        [100%]
app    | 
app    | ============================= 46 passed in 34.38s ==============================
app exited with code 0
```


### Running application

In order to run tests you should run command (from the root of project):

```bazaar
docker-compose -f infra/docker-compose.yaml up -d
```

(Or without `-d` if you want application logs on terminal)

After that you will be able to interact with application on:

http://localhost:5000/

Also you can see documentation on:

* http://localhost:5000/swagger-ui
* http://localhost:5000/redoc

### Stopping the application

In order to stop running application you will need to run:

```bazaar
docker-compose -f infra/docker-compose.yaml down
```
