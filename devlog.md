## Todo List

- [ ] Write serializers
- [ ] Create Postman collection
- [ ] Write seeders
- [ ] Add more languages and interests (read them from a JSON file?)

# Dev log

## `18/02/2022`

First version of model described and revised.

## `22/02/2022`

Dev log started. The next thing to do is creating seeders, then creating serializers and endpoints. I'll probably try to
make the most use from generic classes, etc., and then tailor them to the needs of the project.

- Create seeders: I'll try out django-seed library to create seeders. It uses the Faker library to generate data. It
  also allows us to create and modify the seeding process. If it proves to be ineffective, I'll try out seeding directly
  via Django migrations.

## `22/02/2022`

I've dropped the idea of using django-seed. Instead, I'm creating a new command for manage.py (seed_db) which will
populate the database. This seems much more flexible and easy to use than Django fixtures and Django-seed (I couldn't
figure out how to use the latter effectively).

Edit: this has proved successful so far. The command allows me to create a superuser and any number of users with their
associated friends, languages and interests. I just have to expand it to create messages and channels. 