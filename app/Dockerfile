FROM python:3.7-stretch

WORKDIR /app


RUN pip install pipenv

# Install npm
RUN apt-get update
RUN curl -sL https://deb.nodesource.com/setup_11.x | bash
RUN apt-get update
RUN apt-get install -y nodejs


COPY ./app/Pipfile /app
COPY ./app/Pipfile.lock /app

# --system: Install packages to system's python
# --deploy: Make sure Pipfile.lock is in-sync with Pipfile
# --ignore-pipfile: Use Pipfile.lock for installing
RUN pipenv install --system --deploy --ignore-pipfile


COPY ./app /app
COPY ./${CUB_SIGN_IN_CONFIG} /app/${CUB_SIGN_IN_CONFIG}
RUN npm --prefix static/js install
