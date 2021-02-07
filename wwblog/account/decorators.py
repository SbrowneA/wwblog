# from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponseForbidden
from wwapp.models import (Article, Category,)
from wwapp.handlers import ArticleHandler, CategoryHandler
# from django.core import exceptions
# lower index is superior
from enum import Enum
role_hierarchy = ['admin', 'moderator', 'member', 'general']


class Role(Enum):
    ADMIN = 0
    MODERATOR = 2
    MEMBER = 3
    GENERAL = 4
    # TODO
    #   use enums instead of list

#
# role_hierarchy = {'admin': Role.ADMIN,
#                   'moderator': Role.MODERATOR,
#                   'member': Role.MEMBER,
#                   'general': Role.GENERAL}



"""AUTHENTICATION DECORATORS"""


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


def allowed_user_roles(allowed_roles=[]):
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
    return wrapper_func


def minimum_role_required(min_role_name):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            groups = _get_user_groups(request)
            if groups is not None:
                max_role_name = _get_max_role_name(groups)
                if role_hierarchy.index(max_role_name) <= role_hierarchy.index(min_role_name):
                    return view_func(request, *args, **kwargs)
            return HttpResponseForbidden()
        return wrapper_func
    return decorator


"""ARTICLE DECORATORS"""


def article_edit_privilege(view_func):
    def wrapper_func(request, *args, **kwargs):
        article_id = _get_id_from_request_path(request)
        if _is_article_author(request, article_id) or\
                _is_article_editor(request, article_id) or\
                _is_moderator_or_admin(request):
            return view_func(request, *args, **kwargs)
        # return view_func(request, *args, **kwargs)
        return HttpResponseForbidden()
    return wrapper_func


def article_author_or_moderator(view_func):
    def wrapper_func(request, *args, **kwargs):
        article_id = _get_id_from_request_path(request)
        if _is_article_author(request, article_id) or _is_moderator_or_admin(request):
            return view_func(request, *args, **kwargs)
        HttpResponseForbidden()
    return wrapper_func


def article_published_or_has_editor_privilege(view_func):
    def wrapper_func(request, *args, **kwargs):
        article_id = _get_id_from_request_path(request)
        article = Article.objects.get(article_id=article_id)
        if not request.user.is_authenticated:
            if article.published:
                return view_func(request, *args, **kwargs)
        elif _is_article_author(request, article_id) or \
                _is_article_editor(request, article_id) or \
                _is_moderator_or_admin(request) or \
                article.published:
            return view_func(request, *args, **kwargs)
        HttpResponseForbidden()
    return wrapper_func


"""CATEGORY DECORATORS"""


def category_edit_privilege(view_func):
    def wrapper_func(request, *args, **kwargs):
        article_id = _get_id_from_request_path(request)
        if _is_category_creator(request, article_id) or\
                _is_category_editor(request, article_id) or\
                _is_moderator_or_admin(request):
            return view_func(request, *args, **kwargs)
        # return view_func(request, *args, **kwargs)
        return HttpResponseForbidden()
    return wrapper_func


def category_creator_or_moderator(view_func):
    def wrapper_func(request, *args, **kwargs):
        article_id = _get_id_from_request_path(request)
        if _is_category_creator(request, article_id) or _is_moderator_or_admin(request):
            return view_func(request, *args, **kwargs)
        HttpResponseForbidden()
    return wrapper_func


""" CHECK METHODS
used by the decorators to not repeat logic
these methods check the users Role(Group class)
or their role in relation to the Article/Category.
"""


# AUTHENTICATION CHECK METHODS
# minimum_role_required check method
def _get_max_role_name(groups):
    max_role_i = len(role_hierarchy) - 1
    for group in groups:
        role_position = role_hierarchy.index(group.name)
        if role_position < max_role_i:
            max_role_i = role_position
    return role_hierarchy[max_role_i]


def _get_user_groups(request):
    if request.user.groups.exists():
        return request.user.groups.all()
    else:
        return None


def _is_moderator_or_admin(request):
    groups = _get_user_groups(request)
    if groups is not None:
        max_role_name = _get_max_role_name(groups)
        if max_role_name == "admin" or max_role_name == "moderator":
            return True
    return False


# ARTICLE CHECK METHODS
def _is_article_editor(request, article_id):
    article = Article.objects.get(article_id=article_id)
    editors = ArticleHandler(article).get_editors()
    if editors is not None:
        if request.user in editors:
            return True
    return False


def _is_article_author(request, article_id):
    article = get_object_or_404(Article, article_id=article_id)
    if article.author_id == request.user.id:
        return True
    return False
    # try:
    #     article = Article.objects.get(article_id=article_id)
    #     if article.author_id == request.user.id:
    #         return True
    # except exceptions.ObjectDoesNotExist:
    #     return False
    # return False


def _get_id_from_request_path(request):
    url = request.path
    # print(f"URL: {url}")
    # print(f"LIST: {url.split('/')}")
    # print(f"ID: {url.split('/')[2]}")
    return url.split('/')[2]


# CATEGORY CHECK METHODS
def _is_category_creator(request, category_id):
    cat = get_object_or_404(Category, category_id=category_id)
    if cat.category_creator == request.user.id:
        return True
    return False


def _is_category_editor(request, category_id):
    c = get_object_or_404(Category, category_id=category_id)
    editors = CategoryHandler(c).get_category_editors()
    if editors is not None:
        if request.user in editors:
            return True
    return False
