# moviedialogs api

## Setup

* `pipenv install`
* create `.env` with commands or run manually:
  * `export DATABASE_URI=<dialect://user:password@host/dbname>`
  * `export FLASK_APP=api`
  * `export FLASK_ENV=development` (enable development environment with debug mode)
* `pipenv shell`
* `flask db upgrade`
* `flask seed`

`flask run` to run app on `http://localhost:5000/`

## API Endpoints

|Method | URL | Action |
|-------|-----|--------|
|GET    | /moviedb/api/v0.1/characters/[string:character_id] | Retrieve a character |
|GET    | /moviedb/api/v0.1/conversations/[int:conversation_id] | Retrieve a conversation |
|GET    | /moviedb/api/v0.1/genres/[int:genre_id] | Retrieve a genre |
|GET    | /moviedb/api/v0.1/lines/[string:line_id] | Retrieve a line |
|GET    | /moviedb/api/v0.1/movies/[string:movie_id] | Retrieve a movie |

Movie data includes character and conversation IDs
