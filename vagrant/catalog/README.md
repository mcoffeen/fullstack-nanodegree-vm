# Item Catalog Project

This project is a web application using Flask and SQLAlchemy to create an item catalog storing discs used to play the sport of disc golf.

### Requirements
* Python 2.7
* Flask
* SQLAlchemy

### Before Running `application.py`
1. The database needs to be set up by running `db_setup.py` to create the database and tables.
2. Run `add_collections.py` to create some sample collections and fake users.

### Running `application.py`
* Running the application will create an HTTP server on the localhost listening on port 5000.
* To access the web app, open a web browser and go to `localhost:5000`.

### Loggin In
In order to create collections and add/edit/delete items the user must login using their Google account.