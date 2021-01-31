from django.http import HttpResponse
from django.shortcuts import redirect
from django.http import HttpResponseForbidden


def authentication_required(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('wwapp:login')
    return wrapper_func


def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('wwapp:index')
    return wrapper_func


def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            group = None
            if request.user.groups.exists():
                group = request.user.groups.all[0].name
            if group in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                HttpResponseForbidden()

        return wrapper_func
    return decorator


def active_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_active:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('wwapp:unverified_user')
            # return view_func(request, *args, **kwargs)
    return wrapper_func


def minimum_role_required(min_role):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            if request.user.groups.exists():
                groups = request.user.groups.all()
                max_role = get_max_role(groups)
                if role_hierarchy.index(max_role) <= role_hierarchy.index(min_role):
                    return view_func(request, *args, **kwargs)
            HttpResponseForbidden()
        return wrapper_func
    return decorator


def get_max_role(groups):
    max_role_i = len(role_hierarchy)-1
    for group in groups:
        role_position = role_hierarchy.index(group.name)
        if role_position < max_role_i:
            max_role_i = role_position
    return role_hierarchy[max_role_i]


# lower index is superior
role_hierarchy = ['admin', 'moderator', 'member', 'general']
