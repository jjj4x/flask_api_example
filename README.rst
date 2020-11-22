===============================
Flask REST API Example
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


Build development Docker Image:

.. code-block:: bash

    tox -e build


Spin up the infrastructure:

.. code-block:: bash

    tox -e up


Shutdown the infrastructure:

.. code-block:: bash

    tox -e down


Initialize the database:

.. code-block:: bash

    tox -e init-db


On Models change, make a new migration:

.. code-block:: bash

    tox -e make-migration


Migrate:

.. code-block:: bash

    tox -e migrate


Run Style Guide against the latest code:

.. code-block:: bash

    tox -e style-guide


Run Unit Tests against the latest code:

.. code-block:: bash

    tox -e unit-tests


Run Unit Tests with Coverage:

.. code-block:: bash

    tox -e unit-tests-with-coverage


Show the coverage report:

.. code-block:: bash

    tox -e coverage-report


Generate documentation from code:

.. code-block:: bash

    tox -e docs


Generate OpenAPI JSON specification:

.. code-block:: bash

    tox -e docs-openapi
