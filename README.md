# wwblog

wwblog is a blog web-app built on Django. It implements a number of open-source libraries/apps and free services to
operate.

#### [Check out the live site](https://wwblogs.herokuapp.com/)

<br/>

# Overview

This is a web app hosted on a Heroku Dyno web server and uses their included PostgreSQL database. To make blog posts, it
implements [django-tinymce](https://django-tinymce.readthedocs.io/en/latest/) which is
the [TinyMCE](https://www.tiny.cloud/) WYSIWYG editor for Django. It then saves the users' posts content to an AWS S3
bucket in HTML format.

Users' image uploads are stored on Imgur using the [Imgur API](https://api.imgur.com/) through a fork
of [imgurpython](https://github.com/SbrowneA/imgurpython).

This app includes essential account management functionality including:

- registration
- account activation*
- password reset - *via email if have forgotten their password*
- password change - *if they are able to login*

*When a new user registers, their account will need to be activated by a moderator via the moderator dashboard or a superuser via the admin dashboard.

## Applications & Third Party Implementations

### Installed Apps

The additional installed applications (`INSTALLED_APPS` excluding default Django apps) include the following:

- account - custom user models used for authentication and account management
- wwapp - the core app functionality and data models
- tinymce - provides TinyMCE editor widget to use in forms
- django.contrib.sites - required by tinymce
- django.contrib.flatpages - required by tinymce

 <!-- - storages - used for AWS storage with s3 boto3 implementation -->

### Third Party Libraries

- wwblog uses [Bootstrap 4](https://getbootstrap.com/) for the responsive `base.html` page and some input elements.

- The [DropzoneJS](https://www.dropzonejs.com/)  javascript library is used to make image uploads.

  Basic flow of events:
    1. In the post's edit page, the user opens image upload popup and they drag and drop images the would like to upload
       to the dropzone.
    2. If the format is valid, the images are posted to a backend url which anonymously uploads the image to Imgur
       though the Imgur API.
    3. Once upload is complete the image embed is added to the TinyMCE editor
       <img src="https://cdn.discordapp.com/attachments/736228639875661924/837306999413932112/drag-drop.gif" alt="A demo gif of drag and drop uploads using DropzoneJS" width="70%"/>

# Required Credentials

wwblog uses accesses credentials through environment variables; these are the names they are accessed by in code. (
e.g. `SETTINGS_NAME = os.environ['ENV_VARIABLE_NAME']`)

see: [How To Set Environment Variables](https://www.twilio.com/blog/2017/01/how-to-set-environment-variables.html)

### Required
- django:
    - `WWBLOG_SECRET_KEY`

- AWS *(not required for local deployment of **development** branch)*:
    - `AWS_STORAGE_BUCKET_NAME`
    - `AWS_ACCESS_KEY_ID`
    - `AWS_SECRET_ACCESS_KEY` 
- postgreSQL DB *(not required for local deployment of **development** branch)*:
    - `DATABASE_HOST`
    - `DATABASE_NAME`
    - `DATABASE_PORT`
    - `DATABASE_USER`
    - `DATABASE_PASSWORD`
- imgur:
    - `IMGUR_CLIENT_ID`
    - `IMGUR_REFRESH_TOKEN`
- Gmail:
    - `EMAIL_HOST_USER`
    - `EMAIL_HOST_PASSWORD`

### Optional
- `ALLOWED_HOST` - domain of the host site, not required locally (e.g., "`my-site.com`")
- `ADMIN_EMAIL` - used for the `ADMINS` setting. The app will email this account using the `EMAIL_HOST_USER` with a stack trace similar to debug if the site crashes.
  [see more](https://docs.djangoproject.com/en/3.2/ref/settings/#admins)
  
  Currently, it is only configured for one email address to receive emails, but feel free to fork this repo to add however many you want.

# Getting Credentials

## Gmail
*you will need a Gmail account to complete these steps*

wwblog uses gmail as its email service. Follow the steps in this article to get
your `EMAIL_HOST_PASSWORD`: [Create App-Specific Passwords in Gmail](https://www.lifewire.com/get-a-password-to-access-gmail-by-pop-imap-2-1171882)

## Imgur API Client App
*you will need an Imgur account to complete these steps*

1. login to Imgur and [Register An Imgur client app](https://api.imgur.com/oauth2/addclient)
2. Enter the required details select *"OAuth 2 authorization **without callback** URL"*
3. Make sure to take note of the client id and secret. (You will not need the secret for this but you won't see it
   again)

4. You will now need a refresh token for you account. Visit the following link and log in to authorize your imgur client
   app:

   `https://api.imgur.com/oauth2/authorize?client_id=YOUR_CLIENT_ID&response_type=token`

5. Wait to be redirected and copy the `refresh_token` value from the redirect url.

## AWS Bucket
*you will need an AWS account to complete these steps*
1. Create an AWS account and create a new S3 bucket
    - make sure the bucket is public - since the static files will need to be readable by all users; the user posts will
      be static, however.
2. Use [this config](https://gist.github.com/SbrowneA/c55ca9e6b52a7358f7cce62be195ce29) to set the bucket's CORS
   configuration
3. Create a new IAM group and add a new policy and
   use [this config](https://gist.github.com/SbrowneA/6e0f9d55cda9ac20341d3b1acde5883e) to create your policy.
4. Create and new IAM user:
    1. Enable **programmatic access**
    2. Add this user to the IAM group previously created.
    3. In a secure place, save the new Access Key ID - `AWS_ACCESS_KEY_ID`, and Secret Access Key - `AWS_SECRET_ACCESS_KEY`.

# Local Setup Steps

   *The development branch is configured to run locally without needing to setup an external host server or database.*
1. using your preferred git tool checkout the `development` branch.

2. make sure you have add the **Required Credentials** to your environment variables:

3. Create a `venv` in the project directory according to the runtime specified in `runtime.txt` and activate it.
4. Run `pip install -r requirements.txt` to install all dependencies.


5. In `settings.py`, check the local is SQLite database is un-commented (`db.sqlite3`), and the whole `DATABASES` dict
   for the remote database is commented-out (`postgresql_psycopg2`).
   
    What you should have:
    ```py
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
    ```

6. Setup the database by first running `manage.py makemigrations` followed by `manage.py migrate`
7. Run `coverage run --omit='*/venv/*' manage.py test` and make sure all tests pass
8. Create a superuser with the `manage.py createsuperuser` command

9. run the `manage.py runserver` command to start up the server

10. login to the admin dashboard (`/admin` subdirectory), create the following groups:
    - admin - *required*
    - moderator - *required*
    - member - *required*
    - suspended - *not yet implemented*
    - banned - *not yet implemented*
    
    This step is required because when a user registers they are added to the *member* group automatically.

You're all set to go!

# Heroku Deployment

To complete these instructions will need to complete ***Local Setup Steps***. to successfully deploy this application first make sure you have the all the ***Required Credentials*** Stated above. (database credentials will be generated below) 

1. Create a python app in heroku
2. In the heroku app dashboard, copy all required credentials into the configuration in  settings.
    - database credentials will be generated once the app is deployed

3. In a local instance, checkout the **main** branch and run `collectstatic` to upload the static files to the AWS S3 bucket.
4.  In the AWS Management Console, go to the S3 Bucket previously created, adn set the `static/` object to be **public** and the `media/` object to be **private**.
5. in the heroku app's settings tab add a new configuration variable called `DISABLE_COLLECTSTATIC` with a value of `1`. 
Alternatively, Localy setup Heroku CLI and run `heroku config:set DISABLE_COLLECTSTATIC=1` to prevent `collectstatic` from running each deployment.

     - this command will often timeout due to the duration of upload/AWS slow upload speed and cause deployment to fail.
6. Deploy the app to Heroku from the `main` branch in the repository.
7. Once deployed, a new PostgreSQL DB should attached be in the resources tab. Copy the credentials in to the heroku application's configuration in settings.
8. From a local instance, copy the DB credentials into environment variables and setup the database by first running `makemigrations` followed by `migrate` 
9. go through steps 8 *and* 10 of ***Local Setup Steps*** to complete deployment


# Troubleshooting
- check heroku logs by running `heroku logs --tail --app=app-name` command in the CLI
- make sure `DEBUG = false` on the main branch
- make sure `ALLOWED_HOSTS` includes the applications domain
- make sure the domain has been added to to TinyMCE allowed domains
  
## Live Site: Bad Request (400)
- in `settings.py`, make sure the `ALLOWED_HOSTS` setting is correct. 
  To run locally, only `127.0.0.1` is required; but to run on the  Heroku server, the domain needs to be specified. See
  ***Required Credentials***.

## Live Site: Static Files Not Loading/Forbidden (403)
- make sure the `static/` object in your s3 bucket is public

## Boto3: Access Denied
if you encounter this error:
`(AccessDenied)` when running `manage.py collectstatic`
- make sure bucket is public but the `media/` object is private.
- check if credentials are correct through the AWS CLI - read AWS
  Docs [configure](https://docs.aws.amazon.com/cli/latest/reference/configure/)
  and [list-buckets](https://docs.aws.amazon.com/cli/latest/reference/s3api/list-buckets.html) commands
