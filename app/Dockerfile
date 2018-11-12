FROM python:3.7

RUN mkdir -p /home/project/app
WORKDIR /home/project/app

# Copy both over as a sanity check so we know Pipfile.lock is up to date
COPY Pipfile /home/project/app
COPY Pipfile.lock /home/project/app
RUN pip install pipenv

# --system: Install packages to system's python
# --deploy: Make sure Pipfile.lock is in-sync with Pipfile
# --ignore-pipfile: Use Pipfile.lock for installing
RUN pipenv install --system --deploy --ignore-pipfile

COPY . /home/project/app
