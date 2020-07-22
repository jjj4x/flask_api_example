from pathlib import Path
from os import environ

from setuptools import setup, find_packages

ROOT_PATH = Path(__file__).parent.absolute()
RELEASE = '1.0.0{branch_modifier}{build_number}'
BUILD_NUMBER = environ.get('BUILD_NUMBER', 0)
BRANCH_NAME = environ.get('BRANCH_NAME', 'dev')

if BRANCH_NAME == 'master':
    VERSION = RELEASE.format(branch_modifier='', build_number='')
else:
    VERSION = RELEASE.format(branch_modifier='.dev', build_number=BUILD_NUMBER)


if __name__ == '__main__':
    with open(ROOT_PATH / 'README.rst', encoding='utf8') as fd:
        long_description = fd.read()

    setup(
        name='MYAPP',
        url='https://github.com/jjj4x/flask_classful_api_example.git',
        version=VERSION,
        author='Max Preobrazhensky',
        author_email='max.preobrazhensky@gmail.com',
        description='MYAPP -- Flask-Classful REST API Example',
        long_description=long_description,
        python_requires='>=3.7',
        install_requires=[
            # https://www.sqlalchemy.org/
            'SQLAlchemy',

            # https://marshmallow.readthedocs.io/en/stable/index.html
            'Marshmallow',

            # https://webargs.readthedocs.io/en/latest/index.html
            'WebArgs',

            # https://apispec.readthedocs.io/en/latest/
            # https://dev.to/djiit/documenting-your-flask-powered-api-like-a-boss-9eo
            # https://github.com/Redocly/redoc
            'APISpec[yaml]',
            'APISpec-WEBFrameworks',

            # https://flask.palletsprojects.com/en/master/
            'Flask',
            # https://flask-debugtoolbar.readthedocs.io/en/latest/
            'Flask-DebugToolbar',
            # https://flask-security-too.readthedocs.io/en/stable/
            'Flask-Security-Too',
            # https://flask-jwt-extended.readthedocs.io/en/stable/
            'Flask-JWT',
            # https://marshmallow-sqlalchemy.readthedocs.io/en/latest/
            'Flask-SQLAlchemy',
            # https://flask-migrate.readthedocs.io/en/latest/
            'Flask-Migrate',
            # https://flask-marshmallow.readthedocs.io/en/latest/
            'Flask-Marshmallow[sqlalchemy]',

            # Assumed by third-parties
            'Click',
            'PyYAML',
            'Werkzeug',
        ],
        extras_require={
            'development': [
                'Tox',
                'PyTest',
            ]
        },
        include_package_data=True,
        package_dir={'': 'src'},
        packages=find_packages(where='src'),
    )
