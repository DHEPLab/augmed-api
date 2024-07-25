# AugMed-API

## Local Environment Setup

1. **Install Python**

   Use the following command to install Python:
   ```shell
   brew install python@3.11
   ```
   After installation, verify the new version by running:
   ```shell
   python3 --version
   ```

2. **Install Pipenv**

   Pipenv is used to manage dependencies as it can automatically generate the `Pipfile.lock`, unlike `virtualenv` which requires manual generation of `requirements.txt`.
   ```shell
   pip install pipenv
   ```
   For installing further dependencies, use `pipenv install <package>` instead of `pip install <package>` to manage the dependencies efficiently.

3. **Docker**

   Ensure Docker is installed and running locally on your machine.

4. **Python Path**

   In the root path of the project, set the `PYTHONPATH` by running:
   ```shell
   export PYTHONPATH=$(pwd)
   ```

## Running the Application

To run the application locally, follow these steps:

1. Ensure all dependencies are installed using Pipenv.
2. Start your Docker containers if the application requires any external services like databases.
3. Use the following command to run the application under the ``src``:
   ```shell
   flask run
   ```
   Adjust the command based on your application's entry point if different.

## Testing

### Pytest Naming

Pytest discovers tests following these naming conventions:
```shell
test_*.py
*_test.py
```
For more details, visit [pytest documentation](https://docs.pytest.org/en/latest/explanation/goodpractices.html#test-discovery).

### Running Tests

Execute your tests by running:
```shell
pytest
```
Ensure you are in the project's root directory or specify the tests' path.

## Linting

To maintain code quality and consistency, run linting tools such as flake8 or pylint. Install your chosen linter via pipenv, then run it across your project. For example, with flake8:
```shell
pipenv install flake8
flake8 src
```

## Database Setup and Migrations

### Local Database

To set up the local database, firstly export the var in ``.env`` to local. Then run:
```docker
docker-compose up -d
```

And add a .env file in the root  follow the .env_example

### Database Migration

Database migration scripts are managed with [Flask-Alembic](https://flask-alembic.readthedocs.io/en/latest/) under the `src/migrations` folder.

To modify the schema, use the following commands under the ``src``:
```shell
flask db init  # Only needed the first time to create the migration repository.

flask db migrate -m "Create user table"

flask db upgrade  # Execute this if you pull new changes that alter the schema remotely.
```

## Git Hooks

Configure your local hooks as follows:
```shell
git config core.hooksPath .githooks
```



