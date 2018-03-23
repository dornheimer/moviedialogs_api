import ast
import logging
import os
from sqlalchemy import create_engine
from sqlalchemy.ext import baked
from sqlalchemy.orm import sessionmaker
from mappings import Base, Movie, Genre, Character, Line, Conversation

directory = os.path.abspath(os.path.dirname(__file__))
database_uri = 'sqlite:///' + os.path.join(directory, 'movie_dialogs.sqlite')


def get_data(path):
    with open(path, encoding='latin-1') as f:
        for line in f:
            yield line


def process_line(line):
    split_line = line.split(' +++$+++ ')
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

    table_fields = [c.name for c in Movie.__table__.columns]
    data_stream = prepare_data('corpus/movie_titles_metadata.txt',
                               table_fields)
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

    table_fields = [c.name for c in Character.__table__.columns]
    data_stream = prepare_data('corpus/movie_characters_metadata.txt',
                               table_fields)
    for count, data in enumerate(data_stream, 1):
        character_data, _ = data

        character = Character(**character_data)
        session.add(character)
    session.commit()
    logging.info("inserted %s characters", count)


def insert_lines(session):
    logging.info("inserting lines ...")

    table_fields = [c.name for c in Line.__table__.columns]
    data_stream = prepare_data('corpus/movie_lines.txt', table_fields)
    for count, data in enumerate(data_stream, 1):
        line_data, _ = data

        line = Line(**line_data)
        session.add(line)
        print(f"lines {count}\r", end="")

    session.commit()
    print("")
    logging.info("inserted %s lines", count)


def insert_conversations(session):
    logging.info("inserting conversations ...")

    # Omit id field since it is automatically generated
    table_fields = [c.name for c in Conversation.__table__.columns
                    if c.name != 'id']
    data_stream = prepare_data('corpus/movie_conversations.txt', table_fields)
    first_char_id, second_char_id = None, None

    # 'load' lines into session identity map to make lookup with get() faster.
    # session should usually not be used for caching, but it works here
    lines = session.query(Line).all()

    # use baked query to reduce the python overhead of constructing the SQL
    # statement every single time (no query caching, only minor effect)
    bakery = baked.bakery()
    baked_query = bakery(lambda session: session.query(Line))

    for conv_id, data in enumerate(data_stream, 1):
        conv_data, line_ids = data

        conversation = Conversation(id=conv_id, **conv_data)

        if first_char_id != conversation.first_char_id:
            first_char_id = conversation.first_char_id
            first_char = session.query(Character). \
                filter_by(id=first_char_id).first()

        if second_char_id != conversation.second_char_id:
            second_char_id = conversation.second_char_id
            second_char = session.query(Character). \
                filter_by(id=second_char_id).first()

        for char_obj in (first_char, second_char):
            conversation.characters.append(char_obj)

        for l_id in line_ids:
            # Get looks up primary key in identity map
            line = baked_query(session).get(l_id)
            conversation.lines.append(line)

        print(f"conversations {conv_id}\r", end="")

        session.add(conversation)

    session.commit()
    print("")
    logging.info("inserted %s conversations", conv_id)


def main():
    engine = create_engine(database_uri)

    Session = sessionmaker(bind=engine)
    session = Session()

    # Base.metadata.create_all(engine)

    insert_movies(session)
    insert_characters(session)
    insert_lines(session)
    insert_conversations(session)


if __name__ == '__main__':
    logging.basicConfig(format='[%(levelname)s] %(message)s',
                        level=logging.INFO)

    main()
