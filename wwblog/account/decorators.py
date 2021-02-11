# from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponseForbidden
from wwapp.models import (Article, Category, )
from wwapp.handlers import ArticleHandler, CategoryHandler
# from django.core import exceptions
from .role_validator import (is_moderator_or_admin, _get_user_groups,
                             _get_max_role_name, role_hierarchy)

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
        if _is_article_author(request, article_id) or \
                _is_article_editor(request, article_id) or \
                is_moderator_or_admin(request.user):
            return view_func(request, *args, **kwargs)
        # return view_func(request, *args, **kwargs)
        return HttpResponseForbidden()

    return wrapper_func


def article_author_or_moderator(view_func):
    def wrapper_func(request, *args, **kwargs):
        article_id = _get_id_from_request_path(request)
        if _is_article_author(request, article_id) or is_moderator_or_admin(request.user):
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
                is_moderator_or_admin(request.user) or \
                article.published:
            return view_func(request, *args, **kwargs)
        HttpResponseForbidden()

    return wrapper_func


"""CATEGORY DECORATORS"""


def category_edit_privilege(view_func):
    def wrapper_func(request, *args, **kwargs):
        category_id = _get_id_from_request_path(request)
        if _is_category_creator(request, category_id) or \
                _is_category_editor(request, category_id) or \
                is_moderator_or_admin(request.user):
            return view_func(request, *args, **kwargs)
        # return view_func(request, *args, **kwargs)
        return HttpResponseForbidden()

    return wrapper_func


def category_creator_or_moderator(view_func):
    def wrapper_func(request, *args, **kwargs):
        category_id = _get_id_from_request_path(request)
        if _is_category_creator(request, category_id) or \
                _is_category_editor(request, category_id) or \
                is_moderator_or_admin(request.user):
            return view_func(request, *args, **kwargs)
        HttpResponseForbidden()

    return wrapper_func


# TODO child_category_creator_or_moderator

""" CHECK METHODS
used by the decorators to not repeat logic
these methods check the users Role(Group class)
or their role in relation to the Article/Category.
"""


def _get_id_from_request_path(request):
    url = request.path
    # print(f"URL: {url}")
    # print(f"LIST: {url.split('/')}")
    # print(f"ID: {url.split('/')[2]}")
    return url.split('/')[2]


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
