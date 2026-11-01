Project Overview

Tools Used
Python ver. 3.13
Flask
Flask-SQLAlchemy
SQLAlchemy
Microsoft SQL
PyODBC
Pytest
Ruff
GitHub Actions

Install

Python 3.13
Microsoft SQL Server
SQL Server Management Studio Management
Microsoft ODBC Driver 18 for SQL Server Management
Git

Setup on Local Device
1. Clone the repository:git clone https://github.com/hadys-space/MovieTracker.git
cd MovieTracker

2. Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pytest

Database Setup
The application uses Microsoft SQL Server and  the database MovieTrackerDB

1. To create the database open a 'New Query' and type: CREATE DATABASE MovieTrackerDB;

2. 

Frontend
In order to run your application, type:

  $ cd frontend
  $ flutter run