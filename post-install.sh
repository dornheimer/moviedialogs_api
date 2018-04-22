#!/usr/bin/env bash
CORPUS_URL="http://www.cs.cornell.edu/~cristian/data/cornell_movie_dialogs_corpus.zip"
cd db
wget -nc $CORPUS_URL
unzip -nj ${CORPUS_URL##*/} -d corpus
alembic upgrade head
python seed.py
