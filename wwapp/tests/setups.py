import time
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from account.role_validation import role_hierarchy

User = get_user_model()
from unittest import skip


def setup_superuser() -> User:
    u = User.objects.create_superuser(username="testSuperuser", email="superuser@mail.com", password="superuser1")
    u.save()
    return u


def setup_groups() -> list:
    """creates Groups in the DB and returns them as a list"""
    if Group.objects.all().count() != len(role_hierarchy):
        groups = []
        for role_name in role_hierarchy:
            # permissions are not required
            group = Group.objects.create(name=role_name)
            groups.append(group)
    else:
        return Group.objects.all()
    return groups


# to make dummy users
def create_users(names: list, role_name: str) -> list:
    setup_groups()
    users = []
    i = role_hierarchy.index(role_name)
    g = Group.objects.get(name=role_hierarchy[i])
    for n in names:
        user = User.objects.create_user(username=n, email=f"{n}@mail.com", password=n)
        user.groups.add(g)
        user.save()
        users.append(user)
    return users


def setup_members() -> list:
    """returns a list Users with group member"""
    member_names = ['testAuthor1', 'testAuthor2', 'testAuthor3', 'testAuthor4']
    return create_users(member_names, "member")


def setup_moderators() -> list:
    """returns a list Users with group moderator"""
    mod_names = ['testMod1', 'testMod2', 'testMod3', 'testMod4']
    return create_users(mod_names, "moderator")


def setup_admins() -> list:
    """returns a list Users with group moderator"""
    names = ['testAdmin1', 'testAdmin2', 'testAdmin3', 'testAdmin4']
    return create_users(names, "admin")


def get_micro_time():
    return int(time.time() * 1000)
