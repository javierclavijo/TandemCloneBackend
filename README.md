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