from django.shortcuts import render
from django.http import Http404, HttpResponse
from .models import Article, User\
    # , ArticleEditor
from wwblog import models

def index(request):
    latest_articles = models.get_latest_articles(count=5)
    values = {
        'latest_articles_list': latest_articles,
    }
    return render(request, "wwblog/index.html", values)


def open_article(request, article_id):
    article = Article.objects.get(article_id=article_id)
    values = {
        'article': article,
        'article_text': article.__str__(),
    }
    return render(request, "wwblog/open_article.html", values)


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
        return render(request, "wwblog/edit_article.html", values)
    except Article.DoesNotExist:
        raise Http404("This post is private or does not exist :/")


def user_details(request, user_id):
    user = User.objects.get(user_id=user_id)
    return HttpResponse(f"User Details\n{user.__str__()}")


def login(request):
    pass