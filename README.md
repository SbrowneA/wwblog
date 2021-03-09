# WWBlog
 A blog web app made using the Django framework

formatting docs: 
https://docs.github.com/en/github/writing-on-github/basic-writing-and-formatting-syntax

 ## Setup Steps
 1. create a `venv` according to the runtime specified in `runtime.txt` and activate it
 2. Run `pip install -r requirements.txt` to install all dependencies.

 3. Setup the database by first running `makemigrations` followed by `migrate`
 4. Create a superuser with the `createsuperuser` command
 5. In the admin dashboard, create the following groups:
    - admin - *required*
    - moderator - *required*
    - member - *required*
    - suspended - *not yet implemented*
    - banned - *not yet implemented*
    This is required because when a user registers they are added to the member group automatically.
6. 


## Heroku Setup Steps
Steps `1-2` of **Setup Steps** are automatically executed so they can be ignored


- copy all required credentials into the configuration in settings.
    #### This includes:
    - AWS
    - postgreSQL DB
    - django (secret key)
    - imgur - *not yet implemented*
- run `collectstatic` locally to upload files to the AWS bucket
- make sure the domain has been added to to TinyMCE allowed domains


- go through steps `3-x` to complete setup


## Debugging
- check heroku logs by running `heroku logs --tail --app=app-name` command in the CLI
- set `DEBUG = false`
- make sure `ALLOWED_HOSTS` includes the applications domain

### Access Denied 
if you encounter this error: 
`(AccessDenied)`

- make sure bucket is public but the `media/` object is private
- check if credentials are correct through the AWS CLI *walk-through link*