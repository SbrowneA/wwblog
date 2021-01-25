from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from django.http import Http404, HttpResponse, HttpResponseRedirect
# from .models import *
from . import forms


def index(request):
    # latest_articles = ArticleHandler.get_latest_articles(count=5)
    # latest_articles = Article.objects.order_by('-pub_date')[:int(5)]
    # projects = Category.get_root_categories()

    values = {
        # "latest_articles_list": latest_articles,
        # "categories": projects,
    }

    # projects = Category.objects.filter(category)
    # if len(sub_cats) == 0:
    #     sub_cats = -1
    return render(request, "wwapp/index.html", values)


def login(request):
    if request.method == "POST":
        form = forms.Login(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            # return HttpResponseRedirect("/")
    else:
        form = forms.Login()
        # form.username = "ads"
        # form.password = ""
        # return HttpResponseRedirect("/login/")
    values = {
        'form': form,
    }
    return render(request, 'wwapp/login.html', values)
#
# def editor_test(request):
#     form = forms.TinyMCE
#     values = {
#         'form': form
#     }
#     if request.POST:
#         pass
#
#     return render(request, "wwapp/editor_tests.html", values)
#

from .handlers import *
# def upload_test(request):
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
#
#
#
#
# def browse_articles(request):
#     return HttpResponse(f"articles")
#
#
# def browse_users(request):
#     return HttpResponse(f"users")
#
#
# def browse_categories(request):
#     return HttpResponse(f"categories")
#
#
# def open_article(request, article_id):
#     # article = get_object_or_404(Article, article_id=article_id)
#     # article = Article.objects.get(article_id=article_id)
#     values = {
#         'article': article,
#         'article_text': article.__str__(),
#     }
#     return render(request, "wwapp/open_article.html", values)
#
#
# def edit_article(request, article_id):
#     try:
#         article = Article.objects.get(article_id=article_id)
#         # article = get_object_or_404(Article, article_id=article_id)
#         editors = article.get_editors()
#         values = {
#             'article': article,
#             'article_text': article.__str__,
#             'editors': editors,
#             'editors_count': len(editors)
#         }
#         return render(request, "wwapp/edit_article.html", values)
#     except Article.DoesNotExist:
#         raise Http404("This post is private or does not exist :/")
#
#
# def user_details(request, user_id):
#     user = get_object_or_404(User, user_id=user_id)
#     # user = User.objects.get(user_id=user_id)
#     return HttpResponse(f"User Details\n{user.__str__()}")
#
#

#
#
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
#
#
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
