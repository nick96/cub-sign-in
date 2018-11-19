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
`redis <https://redis.io/>`_.

The environment variables are configured through the :code:`.dev.env` and
:code:`.env` files. :code:`.dev.env` is intended for development use only and is
not secure for production (mainly in that it requires allows http
calls for OAuth authentication). The :code:`docker-compose.override.yml`
file uses :code:`.dev.env`. For production you will have to use

.. code:: bash

    docker-compose -f docker-compose.yml build && docker-compose -f docker-compose.yml up

To run the application you can simply run

.. code:: bash

    docker-compose build && docker-compose up

This will build and run the different docker image's required to run
the application.

