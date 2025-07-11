# The AugMed App (Backend API)

AugMed is a web application, built for the UNC-Chapel Hill DHEP Lab, that allows the lab to collect data from participants in a user-friendly way. The app is designed to be used on any devices, and it allows participants to answer questions about their judgements for cases with potential Colorectal Cancer (CRC). The app is built using React, and the backend API is built using Flask and Python.

**Live Website**: **[https://augmed1.dhep.org/](https://augmed1.dhep.org/).**

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![AWS RDS](https://img.shields.io/badge/AWS%20RDS-527FFF?style=for-the-badge&logo=amazon-rds&logoColor=white)
![AWS S3](https://img.shields.io/badge/AWS%20S3-8C4FFF?style=for-the-badge&logo=amazon-s3&logoColor=white)
![AWS ECR](https://img.shields.io/badge/AWS%20ECR-F58534?style=for-the-badge&logo=aws&logoColor=white)
![AWS ECS](https://img.shields.io/badge/AWS%20ECS-FF5A00?style=for-the-badge&logo=aws&logoColor=white)
![AWS ALB](https://img.shields.io/badge/AWS%20ALB-232F3E?style=for-the-badge&logo=amazon-aws&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-37814A?style=for-the-badge&logo=celery&logoColor=white)
![Alembic](https://img.shields.io/badge/Alembic-000000?style=for-the-badge&logo=alembic&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-3E8EDE?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-003B57?style=for-the-badge&logo=mysql&logoColor=white)
![pytest](https://img.shields.io/badge/pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)
![Pipenv](https://img.shields.io/badge/Pipenv-343434?style=for-the-badge&logo=pipenv&logoColor=white)
![Flake8](https://img.shields.io/badge/Flake8-000000?style=for-the-badge&logo=flake8&logoColor=white)
![Pylint](https://img.shields.io/badge/Pylint-0D5BFF?style=for-the-badge&logo=pylint&logoColor=white)
![Shell](https://img.shields.io/badge/Shell-4EAA25?style=for-the-badge&logo=gnu-bash&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Docker Compose](https://img.shields.io/badge/Docker%20Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Terraform](https://img.shields.io/badge/Terraform-7B42BC?style=for-the-badge&logo=terraform&logoColor=white)
![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white)
![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)
![Postman](https://img.shields.io/badge/Postman-FF6C37?style=for-the-badge&logo=postman&logoColor=white)

> [!NOTE]
> **Frontend Repository**: **[DHEP Lab AugMed Frontend](https://github.com/DHEPLab/augmed-app).**

## Local Environment Setup

Clone the repository if you haven't done so already, then follow these steps to set up your local environment:

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

> [!IMPORTANT]
> Ensure you have activated your pipenv shell by running `pipenv shell`.

1. Ensure all dependencies are installed using Pipenv.
   ```bash
   pipenv install
   ```
2. Start your Docker containers if the application requires any external services like databases.
3. Use the following command to run the application under the ``src`` directory:
   ```shell
   flask run
   ```
   Adjust the command based on your application's entry point if different.
4. Alternatively, run the following command to start the application, at the root path of the project if there is any port conflict on your machine:
   ```shell
   flask run --host=127.0.0.1 --port=5001
   ```

> [!IMPORTANT]
> If your frontend is also running, ensure it is configured to communicate with this backend API. You may need to set the API URL in your frontend configuration.
> Also, you might need to use CORS (Cross-Origin Resource Sharing) if your frontend and backend are served from different origins. You can use the `flask-cors` package to handle this:
> ```shell
> pipenv install flask-cors
> ```
> Then, in `src/__init__.py`, add:
> ```python
> from flask_cors import CORS
> # Then, after declaring `app` in the same file:
> CORS(app, origins=["http://localhost:3000"], supports_credentials=True, expose_headers=["Authorization"],)
> ```
> This will allow your frontend to make requests to the backend without running into CORS issues.

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

## Black Formatting

It is highly encouraged to use [Black](https://black.readthedocs.io/en/stable/) for code formatting before every commit. You can run it as follows:

```shell
pipenv run black .
```

Run this inside a pipenv shell, from the root directory of the project. This will format all Python files in the project.

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

> [!IMPORTANT]
> When you run `flask db migrate`, it generates a new migration script in the `src/migrations/versions` directory. Review this script to ensure it accurately reflects the changes you made to the models. If necessary, modify the script before running `flask db upgrade`.
> This is very crucial because the migration script might contain errors or false commands, like `drop_table`, which can lead to data loss. Always double-check the generated migration script before applying it.

## Git Hooks

Configure your local hooks as follows:
```shell
git config core.hooksPath .githooks
```

This will ensure that your local git hooks are used instead of the default ones. You can find the hooks in the `.githooks` directory.

## Deployment

The application is deployed using Docker and AWS services. The deployment process involves building Docker images, pushing them to AWS ECR, and deploying them to AWS ECS.

Specifically, the application is deployed to an AWS ECS cluster using Fargate. The deployment process is automated using GitHub Actions, which builds the Docker image, pushes it to ECR, and updates the ECS service.

It also uses Terraform to manage the infrastructure as code. 

> [!TIP]
> **Visit the [augmed-infra repository](https://github.com/DHEPLab/augmed-infra) for more details on the infrastructure setup and deployment process.**

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.
