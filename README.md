# movie dialogs db setup

read data from movie dialogs corpus into a database. uses SQLAlchemy with Alembic. compatible with SQLite and PostgreSQL.

* clone repo
* `pip install -r requirements.txt`
* download the Cornell Movie-Dialogs Corpus from [here](http://www.cs.cornell.edu/~cristian/Cornell_Movie-Dialogs_Corpus.html) and extract files into `project_root/corpus`
* for PostgreSQL: start server on localhost and create database, change `database_uri` in `create_db.py` accordingly
* `cd` into project folder and run `alembic upgrade head` to create database tables
* run `create_db.py`
