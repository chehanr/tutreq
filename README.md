# tutreq

A system to create and manage tutorial requests at ACBT.

## Requirements

- Python 3.6.x
- PostgreSQL

## Installation

    git clone https://github.com/chehanr/tutreq.git && cd tutreq
    virtualenv ENV
    ENV/Scripts/activate
    pip install -r requirements.txt

Rename `.env.sample` to `.env` and provide the variables.

    python manage.py migrate
    python manage.py collectstatic
    python manage.py createsuperuser
    python manage.py runserver

## Deploying to Heroku

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/chehanr/tutereq)

- Set the necessary environment variables.
- Run the above mentioned Django commands.

## TODO

- Upgrade Bootstrap/ fix styling.
- Change PDF generation template.
- General fixes.
- ...