[![Build Status](https://travis-ci.com/dornheimer/moviedialogs_db.svg?branch=master)](https://travis-ci.com/dornheimer/moviedialogs_db)

# moviedialogs api

RESTful API for retrieving data provided by the [Cornell Movie-Dialogs Corpus](www.cs.cornell.edu/~cristian/Cornell_Movie-Dialogs_Corpus.html) (Cristian Danescu-Niculescu-Mizil and Lillian Lee).

## Setup

install `pipenv`:

    pip install pipenv

install project dependencies:

    pipenv install

create `.env` with commands or run manually:

    export DATABASE_URI=<dialect://user:password@host/dbname>
    export FLASK_APP=api

    # enable development environment with debug mode
    export FLASK_ENV=development

download corpus data and set up the database:

    python setup.py postinstall

## Start

`flask run` to run app on `http://localhost:5000/`

## API Endpoints

|Method | URL | Action |
|-------|-----|--------|
|GET    | /api/characters/[string:character_id] | Retrieve a character |
|GET    | /api/conversations/[int:conversation_id] | Retrieve a conversation |
|GET    | /api/genres/[int:genre_id] | Retrieve a genre |
|GET    | /api/lines/[string:line_id] | Retrieve a line |
|GET    | /api/movies/[string:movie_id] | Retrieve a movie |

Movie data includes character and conversation IDs
