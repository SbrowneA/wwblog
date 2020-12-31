from django.db import models

from django.db import models


def get_latest_articles(count):
    latest_articles = Article.objects.order_by('-pub_date')[:int(count)]
    return latest_articles


def get_article_editors(article_id):
    return []
#     editors = []
#     try:
#         editors = ArticleEditor.objects.filter(article_id=article_id)
#     except():
#         pass
#     return editors


class User(models.Model):
    user_id = models.AutoField(primary_key=True, null=False)
    username = models.CharField(max_length=14, null=False)

    class Meta:
        indexes = [
            models.Index(fields=['username'])
        ]

    def __str__(self):
        output = f"User ID: {self.user_id}" \
                 f"Username: {self.username}"
        return output


class Article(models.Model):
    article_id = models.AutoField(primary_key=True)
    article_title = models.CharField(max_length=45, default=None, blank=True, null=True)
    pub_date = models.DateTimeField(default=None)
    # populate with -  default=timezone.now - from django.utils.timezone.now()
    # edit_date = models.DateField(auto_now=True)
    # can be used instead auto_now_add = True,
    creation_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.PROTECT)
    visits = models.IntegerField(default=0)
    published = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['article_title']),
            models.Index(fields=['author']),
        ]

    def __str__(self):
        output = f"\n - ID: {self.article_id}" \
                 f"\n - Title: {self.article_title}" \
                 f"\n - Author: {self.author.username}" \
                 f"\n - Creation Date: {self.pub_date}"
        return output


class ArticleEditor(models.Model):
    # placeholder_id = models.AutoField(primary_key=True)

    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
    )
    editor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    class Meta:
        models.UniqueConstraint(fields=['article', 'editor'], name="article_editor_unique", )
        # DEPRECATED
        # unique_together = (('article_id', 'editor_id'),)

    def __str__(self):
        article = Article.objects.get(article_id=self.article_id)
        editor = User.objects.get(user_id=self.editor_id)

        output = f"Article\n{article.__str__()}" \
                 f"Editor\n{editor.__str__()}"
        return output
