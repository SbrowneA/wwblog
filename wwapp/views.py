import os
import traceback
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
# from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from django.http import (
    # Http404,
    HttpResponse,
    # HttpResponseRedirect
)
# from wwblog import settings
from . import forms
# from django.utils.translation import gettext as _
from account.decorators import (
    # authentication_required,
    # unauthenticated_user,
    # allowed_user_roles,
    # active_user,
    minimum_role_required,
    article_edit_privilege,
    article_author_or_moderator,
    category_edit_privilege,
    category_creator_or_moderator,
)
from .handlers import (
    ArticleHandler, CategoryHandler,
    # ImageHandler
)
# , create_new_article as new_article_handler
from django.db import IntegrityError
import logging
from . import imgur
from .models import (Article,
                     Category)
from wwblog.storages import MediaStorage
from django.core.mail import send_mail

User = get_user_model()


def index(request):
    latest_articles = ArticleHandler.get_latest_published_articles(count=5)
    projects = CategoryHandler.get_all_projects()
    values = {
        "latest_articles_list": latest_articles,
        "active_projects": projects
    }
    return render(request, "wwapp/index.html", values)


@login_required
@minimum_role_required(min_role_name='member')
def create_new_article(request):
    article = ArticleHandler.create_new_article(request.user)
    return redirect('wwapp:edit_article', article_id=article.article_id)


# dev only remove for production
# from django.views.decorators.clickjacking import xframe_options_exempt


# @xframe_options_exempt
def open_article(request, article_id):
    article = get_object_or_404(Article, article_id=article_id)
    a_handler = ArticleHandler(article)
    article_text = a_handler.get_article_content()

    values = {
        'article': article,
        'article_text': article_text,
        'secret_note': None
    }
    if article.published:
        values['article_category'] = a_handler.get_parent_category()
    if request.user.is_authenticated:
        values['has_editor_privilege'] = a_handler.has_editor_privilege(request.user)
        secret = a_handler.get_latest_version().secret_note
        values['secret_note'] = secret
    print("date", str(article.creation_date))
    # article_url = a_handler.get_latest_version_url()
    # if article_url is not None:
    #     values['article_url'] = article_url

    return render(request, "wwapp/open_article.html", values)


@login_required
@article_edit_privilege
def edit_article(request, article_id):
    article = get_object_or_404(Article, article_id=article_id)
    values = {
        'article': article,
    }
    # get author and editors
    a_handler = ArticleHandler(article)
    # c_handler = CategoryHandler()
    # editors = handler.get_editors()
    loaded_content = a_handler.get_article_content()
    secret_note = a_handler.get_latest_version().secret_note
    if secret_note is None:
        secret_note = ""
    form = forms.ArticleEdit(request.POST or None, initial={
        'content': loaded_content,
        'title': article.article_title,
        'secret_note': secret_note})

    if article.published:
        parent_a = a_handler.get_parent_article()
        if parent_a is not None:
            values['parent_article'] = parent_a.article_title
        parent_c = a_handler.get_parent_category()
        if parent_c is not None:
            values['parent_category'] = parent_c.category_name
    else:
        choices = [("", "-----------")]
        choices += CategoryHandler.get_publish_to_choices_for_user(request.user)
        form.fields['publish_to_select'].choices = choices
    values['form'] = form
    if request.method == "POST":
        if form.is_valid():
            # save
            article.article_title = form.cleaned_data.get("title")
            ver = a_handler.get_latest_version()
            secret_note = form.cleaned_data.get("secret_note")
            # secret_note = ""
            ver.secret_note = None if secret_note == "" else secret_note
            # result = 'is  none' if secret_note == '' else 'has something'
            # print(result)
            ver.save()
            article.save()
            content = form.cleaned_data.get("content")
            if not a_handler.save_article_content(content):
                form.add_error(None, "There was an error saving!")
                logging.error(f"{edit_article.__name__} - save "
                              f"-> ArticleHandler.save_article_content() failed to return True")

            if request.POST.get("publish"):
                value = str(request.POST["publish_to_select"])
                if value == "" or None:
                    form.add_error("publish_to_select", "Please select an option to publish to")
                else:
                    content_type, content_id = value.split("-")[0], value.split("-")[1]
                    if content_type == "article":
                        article = get_object_or_404(Article, article_id=content_id)
                        print(f"Publishing to {article}")
                        a_handler.publish_as_child_article(article)
                    else:
                        cat = get_object_or_404(Category, category_id=content_id)
                        print(f"Publishing to {cat}")
                        a_handler.publish_article(cat)
                # redirect so that the html refreshes
                return redirect("wwapp:edit_article", article_id)
            # save first
            # code to publish
        # elif request.POST.get("draft"):
        #     a_handler.draft_article()
        # elif request.POST.get("save"):
        # code to save already executed
        # print("save")
    # values['form'] = form
    return render(request, "wwapp/edit_article.html", values)


@login_required
@article_author_or_moderator
def draft_article(request, article_id):
    a = get_object_or_404(Article, article_id=article_id)
    if a.published:
        ArticleHandler(a).draft_article()
    return redirect('wwapp:edit_article', article_id)


@login_required
@article_author_or_moderator
def delete_article(request, article_id):
    a = get_object_or_404(Article, article_id=article_id)
    ArticleHandler(a).delete_article()
    return redirect('wwapp:manage_own_content')


@login_required
@minimum_role_required("member")
def create_project(request):
    proj = CategoryHandler.create_project(request.user)
    return redirect('wwapp:edit_category', proj.category_id)


@login_required
@category_edit_privilege
# @category_creator_or_moderator
def edit_category(request, category_id):
    c = get_object_or_404(Category, category_id=category_id)
    c_handler = CategoryHandler(c)
    values = {
        "category": c,
        "category_type": c.category_type.lower().capitalize(),
        "child_articles": c_handler.get_child_articles(),
    }
    if c_handler.get_child_category_type() is not None:
        values["child_category_type"] = c_handler.get_child_category_type().lower().capitalize()
    if len(c_handler.get_child_categories()) > 0:
        values["child_categories"] = c_handler.get_child_categories()
    # if request.method == "GET":
    #     form = forms.CategoryEdit()
    if request.method == "POST":
        form = forms.CategoryEdit(request.POST)
        if form.is_valid():
            if request.POST.get("add"):
                try:
                    new_cat_name = form.cleaned_data.get("new_category_name")
                    # print(f"Name: {new_cat_name}")
                    if new_cat_name != "":
                        new_cat = Category.objects.create(category_name=new_cat_name, category_creator=request.user)
                        c_handler.add_child_category(new_cat)
                        values["child_categories"] = c_handler.get_child_categories()
                    else:
                        form.add_error("new_category_name",
                                       f"This {c_handler.get_child_category_type().lower().capitalize()}"
                                       f" name is invalid")
                except IntegrityError:
                    form.add_error("new_category_name",
                                   f"The {c_handler.get_child_category_type().lower().capitalize()}"
                                   f" name must be unique globally")
            if request.POST.get("save"):
                try:
                    cat_name = form.cleaned_data.get("category_name")
                    if cat_name != "" or None:
                        cat_description = form.cleaned_data.get("category_description")
                        if cat_description != "":
                            c.category_description = cat_description
                        c.category_name = cat_name
                        c.save()
                        values["category"] = c
                    else:
                        form.add_error("category_name", f"{c.category_type.lower().capitalize()} cannot be empty")

                except IntegrityError:
                    form.add_error("category_name",
                                   f"{c.category_type.lower().capitalize()} name must be unique")
    else:
        form = forms.CategoryEdit(
            initial={"category_name": c.category_name, "new_category_name": "",
                     "category_description": c.category_description}
        )
    values["form"] = form
    return render(request, "wwapp/edit_category.html", values)


@login_required
@category_creator_or_moderator
def delete_category(request, category_id: int):
    cat = get_object_or_404(Category, category_id=category_id)
    CategoryHandler.delete_category(cat)
    parent_id = request.session.get("parent_category_return") or None
    if parent_id is not None:
        request.session.delete('parent_category_return')
        # TODO test
        # print("redirecting to parent")
        return redirect(edit_category, parent_id)
    # print("redirecting to manage page")
    return redirect('wwapp:manage_own_content')


@login_required
@category_creator_or_moderator
def delete_child_category(request, parent_id: int, child_id: int):
    child_cat = get_object_or_404(Category, category_id=child_id)
    # parent_cat = get_object_or_404(Category, category_id=parent_id)
    CategoryHandler.delete_category(child_cat)
    return redirect(edit_category, parent_id)
    # path = request.path()
    # path = path.split("/")


"""
@login_required
@category_creator_or_moderator
def create_sub_category(request, parent_id):
    # if parent category (parent_id) is not PROJECT or TOPIC the template will give access to this
    parent_cat = get_object_or_404(Category, category_id=parent_id)
    # handler = CategoryHandler(parent_cat)
        # try:
        #     new_name = form.cleaned_data.get('category_name')
        #     new_cat = Category.objects.create(category_name=new_name)
        #     handler.add_child_category(new_cat)
        # except IntegrityError:
            # form.add_error(None, f"The new {handler.get_child_category_type()} must have a unique name")
    # TODO
    return redirect(edit_category, parent_id)
    # pass

"""


@login_required
def manage_own_content(request):
    drafted_articles = ArticleHandler.get_user_drafted_articles(request.user)
    published_articles = ArticleHandler.get_user_published_articles(request.user)
    values = {
        "drafted_articles": drafted_articles,
        "published_articles": published_articles,
        # passing user manage_user_content to use the same template
        "user": request.user,
        "user_projects": CategoryHandler.get_user_projects(request.user),
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
        "user_projects": CategoryHandler.get_user_projects(request.user),
    }
    # TODO replace request.user in template with user only use request.user to verify user
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


def open_category(request, category_id):
    category = Category.objects.get(category_id=category_id)
    c_handler = CategoryHandler(category)
    # c_handler.
    # editors = category.get_category_editors()
    # editors_count = len(editors)

    values = {
        'category': category,
        'child_categories': c_handler.get_child_categories(),
        'child_articles': c_handler.get_child_articles(),
        'category_type': category.category_type.lower().capitalize(),
        # 'editors': editors,
        # 'editors_count': editors_count,
    }
    if request.user.is_authenticated:
        values['has_editor_privilege'] = c_handler.has_editor_privilege(request.user)
    if c_handler.get_child_category_type() is not None:
        values["child_category_type"] = c_handler.get_child_category_type().lower().capitalize()
    return render(request, 'wwapp/open_category.html', values)


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
from wwblog.settings import EMAIL_HOST_USER


def send_email_test(request):
    values = {}
    form = forms.TestEmail(request.POST or None)

    if request.method == "POST":
        print("posted")
        if form.is_valid():
            print("valid")
            message = form.cleaned_data.get("body")
            recipient = form.cleaned_data.get("recipient")
            subject = form.cleaned_data.get("subject")
            print(f"sending '{subject}' to {recipient}")
            send_mail(subject=subject, message=message, recipient_list=[recipient], fail_silently=False,
                      from_email=EMAIL_HOST_USER)
            print("sent")
            values['send_success'] = True

    values['form'] = form
    return render(request, 'wwapp/email_test.html', values)


# def image_upload_test(request):
#     items = imgur.start()
#     values = {
#         'image_items': items
#     }

#
#     return render(request, 'wwapp/upload_image_test.html', values)


"""
# @login_required
# @allowed_users(allowed_roles=['moderator'])
def upload_test(request):
    values = {}
    # https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#storage
    if request.POST:
        # new_file = request.FILES['document']
        dir_in_bucket = os.path.join('posts', 'text.txt')

        media_storage = MediaStorage()
        while media_storage.exists(dir_in_bucket):
            dir_in_bucket = os.path.join(dir_in_bucket, '1')
        if media_storage.exists(dir_in_bucket):
            print("already exists")
            # dir_in_bucket = os.path.join(dir_in_bucket, (new_file.name+"1"))

        if not media_storage.exists(dir_in_bucket):
            try:
                file = media_storage.open("posts/test.txt", "w")
                file.write("test file")
                file.close()
            except Exception as ex:
                # logging.error("Upload failed\n")
                print(f"Upload failed\n{traceback.print_exc()}")

            # media_storage.save(dir_in_bucket, new_file)
            # file_url = media_storage.url(dir_in_bucket)
            # return JsonResponse({
            #     'message': 'OK', 'fileUrl': file_url
            # })
            # values['image_url'] = file_url
        # else:
        #     values['image_url'] = None
        # return JsonResponse({
        #     'message': 'Error: file {filename} already exists at {file_directory} in bucket {bucket_name}'.format(
        #         filename=new_file.name,
        #         file_directory=dir_in_bucket,
        #         bucket_name=media_storage.bucket_name
        #     ),
        # }, status=400)

    return render(request, 'wwapp/upload_test.html', values)
"""
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


from django.views.generic import TemplateView
import time

# @login_required()
# class UploadImage(TemplateView):
#     template_name = 'wwapp/drag_and_drop_images.html'

#
# @login_required()
# def test(request):
#     return render(request, 'wwapp/drag_and_drop_images.html')
#
#
# @login_required()
# def upload_local_image(request):
#     if request.method == "POST":
#         image = request.FILES.get('file')
#
#         name = f"image-{time.time()}"
#         print(request.user)
#         ImageHandler.upload_local_image(image, name, request.user)
#
#    # print(request.FILES)
#     return HttpResponse("uploaded")


def activate_users(request):
    # make user
    u = User.objects.get(email="giwar97105@0pppp.com")
    # activate
    User.objects.activate_user(u)
    return HttpResponse(request, "active")
