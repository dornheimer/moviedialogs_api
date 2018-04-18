# movie dialogs db setup

read data from movie dialogs corpus into a database. uses SQLAlchemy with Alembic. compatible with SQLite and PostgreSQL.

* clone repo
* `pip install -r requirements.txt`
* for PostgreSQL: start server on localhost and create database, change `database_uri` in `create_db.py` accordingly
* to download the corpus data and create the database, run `post-install.sh` from inside the project's root folder


[Cornell Movie-Dialogs Corpus](www.cs.cornell.edu/~cristian/Cornell_Movie-Dialogs_Corpus.html) by Cristian Danescu-Niculescu-Mizil and Lillian Lee
