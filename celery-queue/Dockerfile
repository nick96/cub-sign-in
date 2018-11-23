from python:3.7

WORKDIR /queue

RUN pip install pipenv

COPY ./celery-queue/Pipfile /queue
COPY ./celery-queue/Pipfile.lock /queue

# --system: Install packages to system's python
# --deploy: Make sure Pipfile.lock is in-sync with Pipfile
# --ignore-pipfile: Use Pipfile.lock for installing
RUN pipenv install --system --deploy --ignore-pipfile

COPY ./celery-queue/tasks.py /queue
COPY ./prod.cfg /queue/prod.cfg

ENTRYPOINT celery -A tasks worker --loglevel=info
