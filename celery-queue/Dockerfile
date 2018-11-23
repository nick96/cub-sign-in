from python:3.7

COPY Pipfile /queue
COPY Pipfile.lock /queue

WORKDIR /queue

# --system: Install packages to system's python
# --deploy: Make sure Pipfile.lock is in-sync with Pipfile
# --ignore-pipfile: Use Pipfile.lock for installing
RUN pipenv install --system --deploy --ignore-pipfile

COPY tasks.py /queue

ENTRYPOINT celery -A tasks worker --loglevel=info
