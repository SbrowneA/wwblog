import os
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, HttpResponse, HttpResponseRedirect
from . import forms
from account.decorators import (authentication_required,
                                unauthenticated_user,
                                allowed_user_roles,
                                active_user,
                                minimum_role_required,
                                article_edit_privilege,
                                article_author_or_moderator,
                                category_edit_privilege,
                                category_creator_or_moderator,
                                )
from .handlers import ArticleHandler, CategoryHandler
# , create_new_article as new_article_handler
from . import imgur
from .models import (Article,
                     Category)

User = get_user_model()


def index(request):
    latest_articles = ArticleHandler.get_latest_published_articles(count=5)
    # projects = Category.get_root_categories()

    values = {
        "latest_articles_list": latest_articles,
        # "categories": projects,
    }

    # projects = Category.objects.filter(category)
    # if len(sub_cats) == 0:
    #     sub_cats = -1
    return render(request, "wwapp/index.html", values)


@login_required
@minimum_role_required(min_role_name='member')
def create_new_article(request):
    handler = ArticleHandler.create_new_article(request.user)
    return redirect('wwapp:edit_article', article_id=handler.article.article_id)


def open_article(request, article_id):
    article = get_object_or_404(Article, article_id=article_id)
    values = {
        'article': article,
        'article_text': article.__str__(),
    }
    return render(request, "wwapp/open_article.html", values)


@login_required
@article_edit_privilege
def edit_article(request, article_id):
    # get article
    article = get_object_or_404(Article, article_id=article_id)
    # get author and editors
    handler = ArticleHandler(article)
    # editors = handler.get_editors()
    # get latest version content
    loaded_content = handler.get_article_content
    secret_note = handler.get_latest_version().hidden_notes
    projects = CategoryHandler.get_user_projects(request.user)
    if secret_note is None:
        secret_note = ""
    form = forms.ArticleEdit(request.POST or None, initial={
        'content': loaded_content,
        'title': article.article_title,
        'secret_note': secret_note})
    # TODO
    values = {
        'form': form,
        'article': article,
    }

    if form.is_valid():
        if "publish_article" in form.data:
            print("sum sum")
            # save first
            # code to publish
            pass

        if "save" in form.data:
            print("save")
            pass
            # code to save
        article.article_title = form.cleaned_data.get("title")
        ver = handler.get_latest_version()
        ver.hidden_notes = form.cleaned_data.get("secret_note")
        ver.save()
        article.save()
        content = form.cleaned_data.get("content")
        if not handler.save_article_content(content):
            form.add_error(None, "There was an error saving!")

    return render(request, "wwapp/edit_article.html", values)


@login_required
# @must_be_article_author_or_moderator
def delete_article(request, article_id):
    a = get_object_or_404(Article, article_id=article_id)
    handler = ArticleHandler(a)
    handler.delete_article()
    return redirect('wwapp:browse_own_articles')


@login_required
def create_project(request):
    proj = CategoryHandler.create_project(request.user)
    return redirect('wwapp:edit_category', proj.category_id)


@login_required
@category_edit_privilege
def edit_category(request, category_id):
    # TODO
    c = get_object_or_404(Category, category_id=category_id)
    c_handler = CategoryHandler(c)
    return render(request, 'wwapp/edit_category.html')


@login_required
@category_creator_or_moderator
def delete_category(request, category_id):
    cat = get_object_or_404(Category, category_id=category_id)
    CategoryHandler.delete_category(cat)
    parent_id = request.session.get("parent_category_return") or None
    if parent_id is not None:
        request.session.delete('parent_category_return')
        redirect(edit_category, parent_id)
    # redirect()


@login_required
@category_creator_or_moderator
def create_sub_category(request, parent_id):
    parent_cat = Category.objects.get(category_id=parent_id)
    new_cat = Category.objects.create()
    # TODO
    pass


@login_required
# @allowed_users(allowed_roles=['moderator'])
def upload_test(request):
    values = {}
    if request.method == "POST":
        # name of input 'document'
        new_file = request.FILES['document']
        fs = FileSystemStorage()
        file_name = fs.save(new_file.name, new_file)
        url = fs.url(file_name)
        values['image_url'] = url
        print(f"File name: {new_file.name}")
        print(f"File size: {new_file.size}")
    return render(request, 'wwapp/upload_test.html', values)


@login_required
def manage_own_content(request):
    drafted_articles = ArticleHandler.get_user_drafted_articles(request.user)
    published_articles = ArticleHandler.get_user_published_articles(request.user)
    values = {
        "drafted_articles": drafted_articles,
        "published_articles": published_articles,
        # passing user manage_user_content to use the same template
        "user": request.user,
    }
    return render(request, 'wwapp/manage_user_content.html', values)


@login_required
@minimum_role_required(min_role_name="moderator")
def manage_user_content(request, user_id):
    user = User.objects.get(id=user_id)
    drafted_articles = ArticleHandler.get_user_drafted_articles(user)
    published_articles = ArticleHandler.get_user_published_articles(user)
    values = {
        "drafted_articles": drafted_articles,
        "published_articles": published_articles,
        "user": user,
    }
    # TODO replace request.user in template with user
    return render(request, 'wwapp/manage_user_content.html', values)


def browse_articles(request):
    return HttpResponse(f"articles")


def browse_users(request):
    return HttpResponse(f"users")


def browse_categories(request):
    return HttpResponse(f"categories")

#
# def user_details(request, user_id):
#     user = get_object_or_404(User, user_id=user_id)
#     # user = User.objects.get(user_id=user_id)
#     return HttpResponse(f"User Details\n{user.__str__()}")


# def open_category(request, category_id):
#     category = Category.objects.get(category_id=category_id)
#     # creator = category.category_creator
#     # sub_cats = category.get_child_categories()
#     # sub_cats_count = len(sub_cats)
#     # articles = category.get_child_articles()
#     # articles_count = len(articles)
#     # editors = category.get_category_editors()
#     # editors_count = len(editors)
#
#     values = {
#         'category': category,
#         # 'category_creator': creator,
#         # 'child_categories': sub_cats,
#         # 'child_categories_count': sub_cats_count,
#         # 'child_articles': articles,
#         # 'child_articles_count': articles_count,
#         # 'editors': editors,
#         # 'editors_count': editors_count,
#     }
#
#     return render(request, 'wwapp/open_category.html', values)


# def edit_category(request, cat_id):
#     category = Category.objects.get(category_id=cat_id)
#     # sub_cats = category.get_child_categories()
#     # sub_cats_count = len(sub_cats)
#     # articles = category.get_child_articles()
#     # articles_count = len(articles)
#     # editors = category.get_category_editors()
#     # editors_count = len(editors)
#
#     values = {
#         'category': category,
#         # 'child_categories': sub_cats,
#         # 'child_categories_count': sub_cats_count,
#         # 'child_articles': articles,
#         # 'child_articles_count': articles_count,
#         # 'editors': editors,
#         # 'editors_count': editors_count,
#     }
#
#     return render(request, 'wwapp/edit_category.html', values)


def image_upload_test(request):
    items = imgur.start()
    values = {
        'image_items': items
    }
    # if request.POST

    return render(request, 'wwapp/upload_image_test.html', values)


# def upload_test2(request):
#     values = {}
#     if request.method == "POST":
#         # name of input 'document'
#         new_file = request.FILES['document']
#         fs = FileSystemStorage()
#         file_name = fs.save(new_file.name, new_file)
#         url = fs.url(file_name)
#         values['image_url'] = url
#         print(f"File name: {new_file.name}")
#         print(f"File size: {new_file.size}")
#     return render(request, 'wwapp/upload_test.html', values)