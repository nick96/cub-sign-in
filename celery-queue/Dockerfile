from python:3.7-stretch

WORKDIR /queue

RUN pip install pipenv

COPY ./celery-queue/Pipfile /queue
COPY ./celery-queue/Pipfile.lock /queue

# --system: Install packages to system's python
# --deploy: Make sure Pipfile.lock is in-sync with Pipfile
# --ignore-pipfile: Use Pipfile.lock for installing
RUN pipenv install --system --deploy --ignore-pipfile

COPY ./celery-queue/cub-sign-in.json /queue/cub-sign-in.json
COPY ./${CUB_SIGN_IN_CONFIG} /queue/${CUB_SIGN_IN_CONFIG}
COPY ./celery-queue/tasks.py /queue
