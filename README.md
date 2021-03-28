# WWBlog
 A blog web app made using the Django framework

formatting docs: 
https://docs.github.com/en/github/writing-on-github/basic-writing-and-formatting-syntax

 ## Local Setup Steps
 1. create a `venv` according to the runtime specified in `runtime.txt` and activate it
 2. Run `pip install -r requirements.txt` to install all dependencies.

 3. Setup the database by first running `makemigrations` followed by `migrate`
 4. Run `coverage run --omit='*/venv/*' manage.py test` and make sure all tests pass
 5. Create a superuser with the `createsuperuser` command
 6. In the admin dashboard, create the following groups:
    - admin - *required*
    - moderator - *required*
    - member - *required*
    - suspended - *not yet implemented*
    - banned - *not yet implemented*
    This is required because when a user registers they are added to the member group automatically.


## Heroku Setup Steps
Steps `1-2` of **Setup Steps** are automatically executed so they can be ignored


1. copy all required credentials from `ced.md` into the configuration in settings.
    #### This includes:
    - AWS
    - postgreSQL DB
    - django (secret key)
    - imgur - *not yet implemented*
    - email variables
2. Run `collectstatic` locally to upload files to the AWS bucket.
3. Go though the [Merge-into-deployment-checklist.md](https://github.com/SbrowneA/wwblog/blob/main/merge-into-deployment-checklist.md)
 in `merge-into-deployment-checklist.md`
4. run `heroku config:set DISABLE_COLLECTSTATIC=1` in the CLI to prevent `collectstatic` from running each deployment.
    - will timeout due to the duration of upload/AWS slow upload speed.
5. Deploy the app to Heroku from the `main` branch in the repository.
6. Once deployed, a new PostgreSQL db should be in the resources tab. Copy the credentials in to the applications configuration in settings.

7. the From a local instance Setup the database by first running `makemigrations` followed by `migrate`Add the database credentials into the app's configuration
8. once the database is set up go through step 6. of **Local Setup Steps**

## Trouble Shooting
- check heroku logs by running `heroku logs --tail --app=app-name` command in the CLI
- set `DEBUG = false`
- make sure `ALLOWED_HOSTS` includes the applications domain
- make sure the domain has been added to to TinyMCE allowed domains

### Access Denied 
if you encounter this error: 
`(AccessDenied)`
- make sure bucket is public but the `media/` object is private
- check if credentials are correct through the AWS CLI *walk-through link*