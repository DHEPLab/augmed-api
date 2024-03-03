# aim-ahead-api

Change git username and password

## local environment setup

1. install python
2. install pipenv
3. colima

`` pipenv install``˜


## db migration

flask db init  # Only needed the first time to create the migration repository
flask db migrate -m "Create user table"
flask db upgrade
