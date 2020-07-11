FROM python:3.7.7-slim-buster as build

MAINTAINER max.preobrazhensky@gmail.com

# setup.py will use them, if they're present
ARG BRANCH_NAME='master'
ARG BUILD_NUMBER

COPY\
    ./LICENSE\
    README.rst\
    MANIFEST.in\
    setup.py\
    /opt/

COPY ./src /opt/src

RUN pip install --upgrade pip setuptools wheel\
    && cd /opt/\
    && python setup.py bdist_wheel -d /build

FROM python:3.7.7-slim-buster

ENV PYTHONUNBUFFERED=1\
    DEBIAN_FRONTEND=noninteractive

COPY --from=build /build /build

RUN apt update -yqq\
    && apt upgrade -yqq\
    && apt install gosu\
    && pip install --upgrade pip setuptools\
    && pip install --find-links /build MYAPP\
    && useradd --system --create-home --user-group --shell /bin/bash myapp

WORKDIR /opt

COPY --chown=myapp:myapp ./docker/entrypoint.sh /

ENTRYPOINT ["/entrypoint.sh"]
