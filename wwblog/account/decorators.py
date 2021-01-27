from django.http import HttpResponse
from django.shortcuts import redirect
from django.http import HttpResponseForbidden


def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('wwapp:login')
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


# def successfully_registered(view_func):
#     def wrapper_func(request, *args, **kwargs):
#         if request['successfully_registered']:
#             return view_func(request, *args, **kwargs)
#         else:
#             return redirect('wwapp:index')
#     return wrapper_func
# # TODO make in active account
