import time
from django.contrib.auth import get_user_model
User = get_user_model()
from unittest import skip


def setup_superuser() -> User:
    return User.objects.create_superuser(username="testSuperuser", email="superuser@mail.com", password="superuser1")


# to make dummy users
def setup_authors():
    authors = []
    author_names = ['testAuthor1', 'testAuthor2', 'testAuthor3', 'testAuthor4']
    for u in author_names:
        user = User.objects.create_user(username=u, email=f"{u}@mail.com", password=u)
        # user = User()
        # user.save()
        authors.append(user)
    return authors


def get_micro_time():
    return int(time.time() * 1000)
