# Merge into deployment checklist
## 1. make sure settings are as required
#### - Set `DEBUG` to `FALSE`
#### - Correct database is in use (PostgreSQL)
#### - Make sure `S3 BUCKETS CONFIG` section is un-commented
#### - Comment out `# STATIC_URL = '/static/'  # dev only`
#### - Use `ctrl+shift+f` to search for key-words such as 'dev'(or 'development'), or 'prod'(or 'production')
#### - comment out `POSTS_ROOT = os.path.join(MEDIA_ROOT, 'posts')`

## 2. Make sure handlers.py is correctly configured
#### - comment out all methods ending with `_local():` and remove their usages.

## 3. Run final checks
#### - Run `manage.py check --deploy` to make sure nothing has been missed
#### - Delete all html files in `media/posts/`
#### - Run `coverage run --omit='*/venv/*' manage.py test` (using SQLite DB)
#### - Run `manage.py collectstatic` and make `static/` dir public in the S3 Console
