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

Edit: As of now, I have ruled out this possibility, as it doesn't seem to provide any benefits (at least for now). I
have defined the serializer for the Channel mode without too much trouble. So there goes another part of the base CRUD.
The next issue is chat serializers. I have not defined chat models, but message models --a chat model would only provide
the advantage of providing a common ID for all messages from the same chat. The challenge now is to implement a
serializer which fetches a channel's or a pair of users' messages, creating the chat. It seems simple at first, but I
haven't been able to identify how to do it exactly. My first approach has been to pass a filtered queryset to the
serializer's message field, but I don't know where the model object is in the serializer class. I'll probably have to
override a method or two. I'll keep looking into it. Once this is done, there only remain the translation and correction
classes, which should be comparatively straightforward to implement. Or maybe not. We'll see.

## `25/02/2022`

It was hard, but I managed to create a chat endpoint in the end. It turns out that I had been placing too much
responsibility into serializers, and the appropriate thing to do was using a controller (in Django-speak, a view). I
have learned that serializers' responsibilities should be limited to simple CRUD operations, and that I should avoid
returning complex queries for serializers --these complex querysets must rather be passed as arguments to serializers
upon instancing them inside controllers. This means that I probably will have to rewrite many serializers and create new
ones (taking into account that I will need endpoints to create and update resources, which I haven't really taken into
account yet).

The next task is to create a controller for user chats, which should be rather straightforward. Then, I probably will
create the endpoints for creating and updating resources. In fact, I'm going to try to list the basic ones:

- User:
    - CRUD:
        - [x] User creation
        - [x] Change username, email and description (partial_update)
        - [x] Change password
        - [x] Update friends (list)
        - [x] Update languages (list)
        - [ ] Update interests (list)
    - Chat:
        - [ ] Send message
        - [ ] Edit message
        - [ ] Delete message
- Channel:
    - CRUD:
        - [ ] Create channel
        - [ ] Update channel
        - [ ] Add user to channel
        - [ ] Remove user from channel
        - [ ] Update user's role
    - Chat:
        - [ ] Send message
        - [ ] Edit message
        - [ ] Delete message

In this process, I will need to verify that the data required and returned by the serializers is correct, that it has an
appropriate format (e.g. string, hyperlink) and that no unnecessary data is sent (i.e. IDs and such).

Regarding other features, especially message translations and corrections, I have decided to implement them later on,
then the project has been fleshed out a bit more. The models are there, and they will be useful eventually, but they
represent features that are quite accessory. So I will set them a side for a bit.

Edit: implementing the user chat view was a bit harder than expected, due mostly to the fact that DRF forces custom
action URLs to use regex instead of the usual Django URL. Also, it wasn't really too well documented. Apparently, it's
easier to do it with nested routers using the drf-nested-routers library. But I didn't want to include a library for
what is potentially a one-off use, and on top of that having to learn the library itself.

So I'm in the process of creating a Postman collection for the project, as the standard API viewer is a bit too basic
for the project's needs. In fact, I may instead install a Swagger documentation model, and use that to try out the
endpoints.

`03/03/2022`

My main objective today will be implementing Swagger documentation in the project. I'm going to try using the
drf-spectacular library.

Edit: I've added the library and it works, but setting up Swagger properly is too much work right now and I'm in a bit
of a hurry. I'll just use Postman for now and add documentation later. So there we go, I'll create the endpoints in the
order stated above.

Edit 2: it was a bit confusing, but I made it. I had to save the user and its related objects directly in the view, as
using the user serializer was too confusing. Sadly, I wasted too much time on it.

Now, on to the user update controller. This one should be straightforward, as I plan to reuse much of the code from the
creation controller. I think I'll opt to do that instead of adding addition/removal endpoints for languages and
interests. Simply fetch the user and run the same operations as in user creation.

Actually, forget about that. It's definitely better to do it the other way. It will need several controllers more, but
they will be much simpler than what I just said.

`04/03/2022`

I'm going to try adding those controllers now. By making them separate, the user may be able to update their profile
through separate API calls, using different fields (instead of a large form for all fields). Besides, updating your
profile is not something you do constantly, so this shouldn't cause any server overhead.

`07/03/2022`

I have to upload the devlog from last Friday, but anyway I was unable to advance a lot. I spent a lot of time trying to
write the user update controllers, and I finally discovered the existence of the partial_update endpoint in Django
Rest's ModelViewSet. But I still wanted to somehow filter the request data to avoid users updating restricted
attributes, and DRF's Request object forbid me from modifying the request object. I'll give it another try.

Edit: well, it wasn't that hard in the end, I just copied ModelViewSet.update and filtered the request's data before
passing it on to the serializer. It involves code duplication, but right now I think it's much more important to get
stuff done and then I'll refactor later. Sadly, I forgot to push the commit with the todo list, but I'll get it later.

Edit 2: I've just added the controller to set an user's friends. It's a bit awkward, as it needs a list of URLs instead
of PKs. But it works, and it seems counter-productive to waste time trying to change that.

I've just added the user's language list update endpoint. It wasn't too hard, as I implemented everything in the URL. An
interesting thing I've realized is that, when using serializers with nested fields, there's no need to update those
fields through the related model. You can update them through the nested fields' serializers, and return the related
model serializer's data.

Edit 3: I've finally added the devlog changes from the other day. I'm going to try to make the rest of the CRUD
endpoints today, following the templates I have created in the ones I have already made. Then, I'll probably write tests
for the CRUD endpoints --I don't want to leave tests aside for too long. And, if I can, I'll add the Swagger
documentation for the endpoints. That will take a while, but the sooner I make it, the better. The chat endpoints can
wait, especially considering that I haven't set up WebSockets yet and don't really know whether those endpoints will be
necessary, at least as regular HTTP controllers (maybe there's a better way to implement sending chat messages, etc.
through WebSockets or something).

And actually, I think I'm going to join the user partial update controllers into a single controller. The code I have
written so far for those endpoints feels like a workaround. I probably should write a serializer exclusively for
updating the user's password and make a single view for that.

[//]: # (TODO: ask mr. Ortega what to do with interest fields --whether I should make them JSONFields)