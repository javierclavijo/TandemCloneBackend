# TandemCloneBackend

Back end for clone of Tandem web app written in Django REST Framework. Developed as final project for web development
degree.

## Deployment (Development)

1. Create and activate a Python virtual environment for the project
2. Install the project's dependencies
    - > `pip install -r requirements.txt`
3. Run migrations to create the project's database
    - > `cd tandem`
    - > `python manage.py migrate`
4. Seed the database
    - > `python manage.py seed_db`
5. Create Redis Docker container for WS communication
    - > `docker run -p 6379:6379 -d --name tandem-ws-store redis:6`