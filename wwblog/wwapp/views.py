from django.shortcuts import render
from django.http import Http404, HttpResponse, HttpResponseRedirect
from .models import Article, User\
    # , ArticleEditor
from wwapp import models
from .forms import Login


def index(request):
    latest_articles = models.get_latest_articles(count=5)
    values = {
        'latest_articles_list': latest_articles,
    }
    return render(request, "wwapp/index.html", values)


def open_article(request, article_id):
    article = Article.objects.get(article_id=article_id)
    values = {
        'article': article,
        'article_text': article.__str__(),
    }
    return render(request, "wwapp/open_article.html", values)


def edit_article(request, article_id):
    try:
        editors = models.get_article_editors(article_id)
        article = Article.objects.get(article_id=article_id)
        values = {
            'article': article,
            'article_text': article.__str__,
            'editors': editors,
            'editors_count': len(editors)
        }
        return render(request, "wwapp/edit_article.html", values)
    except Article.DoesNotExist:
        raise Http404("This post is private or does not exist :/")


def user_details(request, user_id):
    user = User.objects.get(user_id=user_id)
    return HttpResponse(f"User Details\n{user.__str__()}")


def login(request):
    if request.method == "POST":
        form = Login(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            return HttpResponseRedirect("/")
    else:
        form = Login()
        # form.username = "dasdasdasdsaasd"
        # form.password = ""
        # return HttpResponseRedirect("/login/")
    values = {
        'form': form,
    }
    return render(request, 'wwapp/login.html', values)


def category_all(request):
    pass

    # values = {
    #     'root_cats':
    # }

    return render(request)

def category_open():
    pass


def category_edit():
    pass
