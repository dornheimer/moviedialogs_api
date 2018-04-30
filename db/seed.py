#!/usr/bin/env python3
import ast
import logging
import os
from config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import (
    Character,
    Conversation,
    Genre,
    Line,
    Movie,
)

DATABASE_URI = Config.SQLALCHEMY_DATABASE_URI
DIRECTORY = os.path.abspath(os.getcwd())

CORPUS_PATH = os.path.join(DIRECTORY, 'corpus')
CHARACTERS_DATA = 'movie_characters_metadata.txt'
CONVERSATION_DATA = 'movie_conversations.txt'
LINE_DATA = 'movie_lines.txt'
MOVIE_DATA = 'movie_titles_metadata.txt'


def get_data(path):
    with open(os.path.join(CORPUS_PATH, path), encoding='latin-1') as f:
        for line in f:
            yield line


def process_line(line):
    delimiter = ' +++$+++ '
    split_line = line.split(delimiter)
    split_line[-1] = split_line[-1][:-1]  # Remove newline char
    split_line = [(None if item == '?' else item) for item in split_line]
    if split_line[-1] is None:
        return split_line
    if split_line[-1].startswith('[') and not split_line[0].startswith('L'):
        split_line[-1] = ast.literal_eval(split_line[-1])  # Get it as a list
        split_line[-1] = set(split_line[-1])  # Enfore uniqueness of items
    return split_line


def prepare_data(path, table_fields):
    for line in get_data(path):
        data = process_line(line)
        yield {k: v for k, v in zip(table_fields, data)}, data[-1]


def insert_movies(session):
    logging.info("inserting movies ...")
    data_stream = prepare_data(MOVIE_DATA, Movie.file_mapping)

    for count, data in enumerate(data_stream, 1):
        title_data, genres = data
        title = Movie(**title_data)

        for g in genres:
            g_obj = session.query(Genre).filter_by(name=g).first()
            # Create genre if it does not exist yet
            if g_obj is None:
                g_obj = Genre(name=g)
                session.add(g_obj)
            title.genres.append(g_obj)

        session.add(title)

    session.commit()
    logging.info("inserted %s movies", count)


def insert_characters(session):
    logging.info("inserting characters ...")
    data_stream = prepare_data(CHARACTERS_DATA, Character.file_mapping)

    for count, data in enumerate(data_stream, 1):
        character_data, _ = data
        character = Character(**character_data)
        session.add(character)

    session.commit()
    logging.info("inserted %s characters", count)


def insert_lines(session, line_to_conv_mapping):
    logging.info("inserting lines ...")
    data_stream = prepare_data(LINE_DATA, Line.file_mapping)

    for count, data in enumerate(data_stream, 1):
        line_data, _ = data
        conv_id = line_to_conv_mapping[line_data['id']]

        line = Line(conversation_id=conv_id, **line_data)
        session.add(line)
        print(f"lines {count}\r", end="")

    session.commit()
    print("")
    logging.info("inserted %s lines", count)


def insert_conversations(session):
    logging.info("inserting conversations ...")
    data_stream = prepare_data(CONVERSATION_DATA, Conversation.file_mapping)

    # 'load' characters into session identity map to make lookup with get()
    # faster. session should usually not be used for caching, but it works here
    characters = session.query(Character).all()

    line_to_conv_mapping = {}
    characters = {}
    for conv_id, data in enumerate(data_stream, 1):
        conv_data, line_ids = data

        conv = Conversation(id=conv_id, **conv_data)

        for char_id in (conv.first_char_id, conv.second_char_id):
            char = characters.get(char_id, None)
            if char is None:
                char = session.query(Character).get(char_id)
                characters[char_id] = char

            conv.characters.append(char)

        for l_id in line_ids:
            line_to_conv_mapping[l_id] = conv_id

        print(f"conversations {conv_id}\r", end="")

        session.add(conv)

    session.commit()
    print("")
    logging.info("inserted %s conversations", conv_id)
    return line_to_conv_mapping


def clean_records(session):
    real_ids = {'u5784': 'u5783', 'u5786': 'u5785', 'u6564': 'u6563'}

    for dup_char_id, real_char_id in real_ids.items():
        dup_char = session.query(Character).get(dup_char_id)
        real_char = session.query(Character).get(real_char_id)

        for line in dup_char.lines:
            # Delay autoflush to prevent violating foreign key constraint
            with session.no_autoflush:
                line.character_id = real_char.id
                line.character_name = real_char.name

        # Commit to make new character assignment persistent
        session.commit()

        for conv in dup_char.conversations:
            if dup_char_id == conv.first_char_id:
                conv.first_char_id = real_char_id
            else:
                conv.second_char_id = real_char_id

            real_char.conversations.append(conv)

        session.delete(dup_char)
    session.commit()


def main():
    engine = create_engine(DATABASE_URI)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        insert_movies(session)
        insert_characters(session)
        line_to_conv_mapping = insert_conversations(session)
        insert_lines(session, line_to_conv_mapping)
        clean_records(session)
    except:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == '__main__':
    logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.INFO)
    main()
