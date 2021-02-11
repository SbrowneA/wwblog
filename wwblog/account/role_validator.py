from enum import Enum

# lower index is superior
role_hierarchy = ['admin', 'moderator', 'member', 'general']


class Role(Enum):
    ADMIN = 0
    MODERATOR = 1
    MEMBER = 2
    GENERAL = 3
    # TODO
    #   use enums instead of list

# role_hierarchy = {'admin': Role.ADMIN,
#                   'moderator': Role.MODERATOR,
#                   'member': Role.MEMBER,
#                   'general': Role.GENERAL}


# AUTHENTICATION CHECK METHODS
# minimum_role_required check method
def _get_max_role_name(groups):
    max_role_i = len(role_hierarchy) - 1
    for group in groups:
        role_position = role_hierarchy.index(group.name)
        if role_position < max_role_i:
            max_role_i = role_position
    return role_hierarchy[max_role_i]


def _get_user_groups(user):
    if user.groups.exists():
        return user.groups.all()
    else:
        return None


def is_moderator_or_admin(user):
    groups = _get_user_groups(user)
    if groups is not None:
        max_role_name = _get_max_role_name(groups)
        if max_role_name == "admin" or max_role_name == "moderator":
            return True
    return False
