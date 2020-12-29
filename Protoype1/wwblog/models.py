from django.db import models


class User(models.Model):
    user_id = models.AutoField(primary_key=True, null=False)
    username = models.CharField(max_length=14, null=False)

    def __str__(self):
        output = f"User ID: {self.user_id}" \
                 f"Username: {self.username}"
        return output

class Article(models.Model):
    article_id = models.AutoField(primary_key=True)
    article_title = models.CharField(max_length=45, default=None, blank=True, null=True)
    pub_date = models.DateTimeField('publish date')
    # can be used instead auto_now_add = True,
    creation_date = models.DateTimeField('creation date')
    author = models.ForeignKey(User, on_delete=models.PROTECT)
    visits = models.IntegerField(default=0)
    published = models.BooleanField(default=False);

    def __str__(self):
        output = f"\n - ID: {self.article_id}"\
                 f"\n - Title: {self.article_title}"\
                 f"\n - Author: {self.author}"\
                 f"\n - Creation Date: {self.pub_date}"
        return output



class ArticleEditor(models.Model):
    # placeholder_id = models.AutoField(primary_key=True)

    article_id = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
    )
    editor_id = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    class Meta:
        models.UniqueConstraint(fields=['article_id', 'editor_id'], name="article_editor_id",)
        # DEPRECATED
        # unique_together = (('article_id', 'editor_id'),)

    def __str__(self):
        article = Article.objects.get(article_id=self.article_id)
        editor = User.objects.get(user_id=self.editor_id)

        output = f"Article\n{article.__str__()}" \
                 f"Editor\n{editor.__str__()}"
        return output
