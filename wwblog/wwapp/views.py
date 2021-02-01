import os
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect
# from .models import *
from . import forms
from account.decorators import *
from .handlers import ArticleHandler, CategoryHandler
from wwblog.settings import POSTS_ROOT
from . import imgur

User = get_user_model()


def index(request):
    # latest_articles = ArticleHandler.get_latest_articles(count=5)
    latest_articles = Article.objects.order_by('-pub_date')[:int(5)]
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
# @minimum_role_required(min_role_name='member')
def create_new_article(request):
    handler = ArticleHandler.create_new_article(request.user)
    return redirect('wwapp:edit_article', article_id=handler.article.article_id, permanent=True)


def open_article(request, article_id):
    article = get_object_or_404(Article, article_id=article_id)
    values = {
        'article': article,
        'article_text': article.__str__(),
    }
    return render(request, "wwapp/open_article.html", values)


@login_required
@article_edit_privilege_required
def edit_article(request, article_id):
    # # get article
    # article = get_object_or_404(Article, article_id=article_id)
    # # get author and editors
    # handler = ArticleHandler(article)
    # editors = handler.get_editors()
    # # get latest version and load the file
    # # file_name = handler.get_file_name()
    # loaded_content = handler.get_article_content()
    # form = forms.ArticleEdit(request.POST or None, initial={'content': loaded_content})

    values = {
        # 'form': form
    }

    # if form.is_valid():
    #     # form.cleaned_data['content']
    #     print("\n\nPOSTED")
    #     content = form.cleaned_data.get("content")
    #     file_name = f"{article_id}-{handler.get_latest_version().version}.html"
    #     file_dir = os.path.join(POSTS_ROOT, file_name)
    #     with open(file_dir, 'w') as file:
    #         file.write(content)

    return render(request, "wwapp/editor_tests.html", values)


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
