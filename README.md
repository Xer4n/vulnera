# vulnera

Vulnera is  a delibratly vulnerable web application for penetration testers to try out and test.

## Requirements:

- Python 3.8
- PostgreSQL

## Installation guide

1. Clone the repository

Clone the GitHub repository: ``git clone https://github.com/Xer4n/vulnera.git``

2. Setup the PostgreSQL database with the default super user:

Login to PostgreSQL: ``sudo -u postgres psql``
Create the database: ``CREATE DATABASE vulneradb;``
Change the password of the superuser to allow the application to connect to the user: ``ALTER USER postgres WITH PASSWORD "vulnera";``

Note: You can use your own database user, just remember to change the login information in the ``database.py`` file.


3. Install requirements

Enable virtual environment: ``python3 -m venv venv``
Activate: ``source venv/bin/activate``

Install requirements: ``pip install -r requirements.txt``


5. Run the application


