# HCI-Project---Movie-Recommendation
Recommendation based on content

Django is a Python framework, so we must install Latest Python to machine.

To Install Python, go to website https://python.org/downloads/. Download and Install it into your machine. After installation, open the command prompt and check that if the Python version matches the version you installed by executing:

    py –version

After this, we need pip because it is a Python package manager which comes with Python installer, It helps to install and uninstall python packages like Django.

Install Django into your machine with a simple line of code into your command prompt:

    py -m pip install Django

Now, We need Database to store and retrieve data for our application. So, we will install relational database Postgresql. To install Postgres, go to https://www.postgresql.org/download/. Download and Install it into your machine.

Open Postgresql and Create a Database 'hciFinalProject' in it.

Download this zip code and run them into your IDE or command prompt —

To apply changes into database like creating tables for the application, run this command (make sure in the folder 'hci'):

    \employee_project> python manage.py makemigrations project

    \employee_project> python manage.py sqlmigrate 0001

    \employee_project> python manage.py migrate

To run server on your browser where your project will run, run this command:

    python manage.py server

Now click on the link http://127.0.0.1:8000/ in your terminal or command prompt which ever you are using.

You will see a front page to search and create a new user and you can direct to the list pages from this page.
