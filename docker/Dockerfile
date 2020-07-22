FROM python:3.7.7-slim-buster

MAINTAINER max.preobrazhensky@gmail.com

# setup.py will use them, if they're present
ARG BRANCH_NAME='master'
ARG BUILD_NUMBER
ARG UID=1000
ARG GID=${UID}

COPY \
    ./LICENSE \
    README.rst \
    MANIFEST.in \
    setup.py \
    /opt/

COPY ./src /opt/src

WORKDIR /opt

ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

ARG PYTHON_DEPS

RUN apt update -yqq \
    && apt upgrade -yqq \
    && apt install gosu \
    && pip install --upgrade pip setuptools ${PYTHON_DEPS} \
    && pip install --editable '.[development]' \
    && groupadd --gid ${GID} myapp \
    && useradd --uid ${UID} --gid ${GID} --create-home --shell /bin/bash myapp

COPY --chown=myapp:myapp ./docker/entrypoint.sh /

USER myapp

ENTRYPOINT ["/entrypoint.sh"]
