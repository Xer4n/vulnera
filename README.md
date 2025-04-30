# vulnera

Vulnera is  a delibratly vulnerable web application for penetration testers to try out and test.

## Requirements:

- Python 3.8
- PostgreSQL

## Installation guide

1. Clone the repository

Clone the GitHub repository: ``git clone https://github.com/Xer4n/vulnera.git``

2. Setup the PostgreSQL database with the default super user:

``sudo -u postgres psql``
``CREATE DATABASE vulneradb;`` 
Change the password of the superuser to allow the application to connect to the user: ``ALTER USER postgres WITH PASSWORD "vulnera";``


3. Install requirements

4. Run the application


