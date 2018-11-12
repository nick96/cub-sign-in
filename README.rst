===========
Cub sign-in
===========

This is a simple Flask web application that I built for signing in and
out at our scout hall. Though, it can really be used for any sort of
event that requires signing in and out.

The function of this application is to provide a web page where
parent's can sign their children in and out of the activity. It
provides a simple interface to choose the child's name, enter their
own name and enter the signature. Prior to this the admin has already
logged into the site and set whether we're doing sign in or sign
out. The details are written to a Google Sheets document with the
child's name, parent's name and parent's signature.

As writing to Google Sheets is an expensive operation, when a form is
submitted, a task is added to the `Celery
<http://www.celeryproject.org/>`_ task queue which is backed by
`RabbitMQ <https://www.rabbitmq.com/>`_.

To configure this application use a `.env` file which contains the
required environment variables. That is:

- `FLASK_APP`: Name of the file containing the application
- `CELERY_BROKER`: URL of the broker to use for Celery
- `GOOGLE_SHEETS_ID`: Account ID for use with Google Sheets
- `GOOGLE_SHEETS_SECRET`: Secret key for use with Google Sheets
- `USERS_FILE`: File to read user's emails from (this is intended as a poor
  man's invite system)

To run the application you can simply use `docker-compose up .`. This
will build and run the different docker image's required to run the
application.

