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