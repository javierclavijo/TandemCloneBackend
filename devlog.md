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

## `23/02/2022`

I've dropped the idea of using django-seed. Instead, I'm creating a new command for manage.py (seed_db) which will
populate the database. This seems much more flexible and easy to use than Django fixtures and Django-seed (I couldn't
figure out how to use the latter effectively).

Edit: this has proved successful so far. The command allows me to create a superuser and any number of users with their
associated friends, languages and interests. I just have to expand it to create messages and channels.

Edit 2: I have finished the seeder for now, excluding chat message translation and correction classes. It's been a
success. Although it's a bit slow (as it involves quite a lot of iterations), it will definitely provide a solid base
for developing and testing. And if I need the Django fixtures that I mentioned earlier, I can simply
run `python manage.py dumpdata` after running the seeder script.

## `24/02/2022`

The next step is creating serializers for the API's controllers. I have been playing around with them a bit, with some
success. The hardest part at this point will be serializing all the intermediary tables for models. For example, I have
created a serializer for the UserLanguage intermediary model, which includes all fields (this is needed mostly for
serialization), and I have set it as the 'languages' field for the CustomUser serializer. When I retrieve each user
object, I only want to display specific attributes --language and level-- and exclude the user ID and the UserLanguage
object's ID. But seemingly there's no built-in functionality in Django REST Framework for this case. You are apparently
expected to use inheritance, or maybe to override serialization through the serializers' to_representation() methods. I
will opt for the latter approach first, as the first one would force me to create two classes for too many models, thus
polluting the code. Then, if it falls short for any reason, I may take the other approach and create extra serializer
classes for each model.

In fact, some models such as UserInterest don't really require a serializer, as the only required data is the interest's
string. Therefore, they can be represented through a StringRelatedField, foregoing the need to create a serializer class
for them.

I should investigate if there's a better way to store user interests. It seems that the Django Choices classes are a bit
restrictive. Also, it might be better if the user field were a ManyToManyField.