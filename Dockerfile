# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Install pipenv
RUN pip install pipenv

# Copy the Pipfile and Pipfile.lock into the container
COPY Pipfile Pipfile.lock ./

RUN pipenv --python `which python3`

# Install project dependencies
RUN pipenv install --deploy --ignore-pipfile

# Copy the rest of your application's code
COPY . .

# Make port 5000 available to the world outside this container
EXPOSE 5000

WORKDIR ./src

# Run the application
CMD ["pipenv", "run", "flask", "run", "--host=0.0.0.0"]
