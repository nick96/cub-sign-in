FROM python:3.7

WORKDIR /app


RUN pip install pipenv

# Install npm
RUN apt-get update
RUN curl -sL https://deb.nodesource.com/setup_11.x | bash
RUN apt-get update
RUN apt-get install -y nodejs


COPY Pipfile /app
COPY Pipfile.lock /app

# --system: Install packages to system's python
# --deploy: Make sure Pipfile.lock is in-sync with Pipfile
# --ignore-pipfile: Use Pipfile.lock for installing
RUN pipenv install --system --deploy --ignore-pipfile


COPY . /app
RUN npm --prefix static/js install

