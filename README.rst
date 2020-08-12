===============================
Flask-Classful REST API Example
===============================

The reference Flask API example provides insight into:
    * Structuring and Composition
    * Building
    * Source code documentation
    * API documentation
    * Testing
    * Automation (Tox)
    * Using Flask-Marshmallow
    * Using APISpec

Installation
============

Currently the project isn't hosted on PyPI, so you can install it manually.

Development
===========

docker run -it --rm -v $(pwd)/src/myapp:/usr/local/lib/python3.7/site-packages/myapp -p 0.0.0.0:5000:5000  -e FLASK_APP=myapp -e SECRET_KEY=1 flask-classful-api python -u -m flask run

Build development Docker Image:

.. code-block:: bash

    docker build --rm --tag flask-classful-api --file docker/Dockerfile .

If your UID/GID isn't equal 1000, then build for a custom UID/GID:

.. code-block:: bash

    docker build --rm --tag flask-classful-api --build-arg UID=4242 --file docker/Dockerfile .

Run Style Guide against the latest code:

.. code-block:: bash

    docker run --rm -it -v $(pwd):/opt flask-classful-api tox -e style-guide

Run Unit Tests against the latest code:

.. code-block:: bash

    docker run --rm -it -v $(pwd):/opt flask-classful-api tox -e unit-tests

A running PostgreSQL is required:

.. code-block:: bash

    docker-compose up

To auto-generate a new revision file:

.. code-block:: bash

    docker run --rm -it -v $(pwd):/opt flask-classful-api tox -e db migrate

To upgrade to the latest revision:

.. code-block:: bash

    docker run --rm -it -v $(pwd):/opt flask-classful-api tox -e db upgrade

For usage:

.. code-block:: bash

    pip install .

For development:

.. code-block:: bash

    pip install -e .

The environment variables are required:

.. code-block:: bash

    export SQLALCHEMY_DATABASE_URI=postgresql://postgres:postgres@localhost:5555/postgres
    export FLASK_APP=myapp.app

Initialize the database:

.. code-block:: bash

    flask db init

Create superuser account:

.. code-block:: bash

    flask create-user

To collect static into PWD (use COLLECT_STATIC_ROOT to change to location):

.. code-block:: bash

    flask collect

Usage
=====

Test in CLI:

.. code-block:: bash

    curl -w '\n' -iX POST http://127.0.0.1:5000/api/v1/auth -H Content-Type:application/json -d '{"name": "buddy", "password": "123"}'
    curl -w '\n' -iX GET 'http://127.0.0.1:5000/api/v1/users?sort_column=name&flt_name_in_list=mate6,mate7,mate3&flt_roles.name_in_list=zork,bork' -H 'Authorization: Bearer X'
    curl -w '\n' -iX GET 'http://localhost:5000/api/v1/users?flt_roles_role_name_equals=superuser' -H Authorization:'Bearer X'

Checkout Flask-Admin in http://127.0.0.1:5000/admin.

Checkout OpenAPI documentation in http://127.0.0.1:5000/apidocs