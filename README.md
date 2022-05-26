# tandem-backend

Backend for tandem language exchange chat app written in Django REST Framework. Final project for Professional Training
in Web Applications Development (_Grado Superior en Desarrollo de Aplicaciones Web_).

Frontend repo: https://github.com/javierclavijo/tandem-frontend

## Deployment (Development)

1. Create and activate a Python virtual environment for the
   project (https://docs.python.org/3/library/venv.html#creating-virtual-environments)
2. Install the project's dependencies
    - > `pip install -r requirements.txt`
3. Run migrations to create the project's database
    - > `cd tandem`
    - > `python manage.py migrate`
4. Seed the database
    - > `python manage.py seed_db`
5. Create Redis Docker container for WS communication
    - > `docker run -p 6379:6379 -d --name tandem-ws-store redis:6`

### Debugging

To debug the application in PyCharm, a few additional steps are needed:

1. Add the container's interpreter as the project's Python interpreter. Go to Settings -> Project -> Python Interpreter,
   click on the settings icon and then on `Add...`. Select Docker Compose and set compose.yaml as the configuration file
   and 'api' as the service, then click 'OK'.
2. Set DEBUG to 1 in the .env file if it's not already set.
3. Finally, a configuration must be created to run the app inside the container. Instructions can be found here:
   https://www.jetbrains.com/help/pycharm/using-docker-compose-as-a-remote-interpreter.html#run

## Deployment with Docker-compose

`docker network create tandem-network`
`docker compose up --build` (frontend, then backend)
`docker compose exec api python /code/manage.py migrate`
`docker compose exec api python /code/manage.py seed_db`
`docker compose exec api python /code/manage.py collectstatic`

Note: once the app is up in a local environment, it must be accessed from 127.0.0.1 instead of localhost. This is due to
the way the Nginx configuration is set up --the Access-Control-Allow-Origin header, which is required for sessions to
work, is set to the $host variable, which in practice means that it's set to 127.0.0.1, and localhost doesn't work.

# Testing

To test the project, a data fixture must be created to provide data for the tests. To do this, run the following command
from the project's root after seeding the database:
`docker compose exec api python /code/manage.py dumpdata --all > ./tandem/common/fixtures/test_data.json`

This will create a JSON file with the project's current data. On Windows, an error may happen due to the default
encoding used by the shell, which may be fixed by changing the file's encoding to UTF-8. Also, Docker Compose may add
messages before and after the file's content ("failed to get console mode for stdout: The handle is invalid.", "Unable
to close the console"), which must be deleted.