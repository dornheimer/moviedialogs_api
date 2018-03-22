import ast
import logging
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from mappings import (Base, Title, Genre, TitleGenres, Character, Line,
                      Conversation, ConversationLines)

GENRES = {
    'family', 'film-noir', 'documentary', 'history', 'adult', 'horror',
    'music', 'western', 'thriller', 'drama', 'war', 'mystery', 'animation',
    'sport', 'comedy', 'fantasy', 'short', 'musical', 'sci-fi', 'biography',
    'romance', 'adventure', 'action', 'crime'
}


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


def insert_genres(session):
    logging.info("inserting genres ...")
    for genre in GENRES:
        g = Genre(name=genre)
        session.add(g)
    session.commit()
    logging.info("inserted %s genres", len(GENRES))


def insert_titles(session):
    logging.info("inserting titles ...")

    table_fields = [c.name for c in Title.__table__.columns]
    data_stream = prepare_data('corpus/movie_titles_metadata.txt', table_fields)
    for count, data in enumerate(data_stream, 1):
        title_data, genres = data

        title = Title(**title_data)
        session.add(title)

        for g in genres:
            genre_id = session.query(
                Genre.genre_id).filter(Genre.name == g).first()[0]

            title_genre = TitleGenres(movie_id=title_data['movie_id'],
                                      genre_id=genre_id)
            session.add(title_genre)
    session.commit()
    logging.info("inserted %s titles", count)


def insert_characters(session):
    logging.info("inserting characters ...")

    table_fields = [c.name for c in Character.__table__.columns]
    data_stream = prepare_data('corpus/movie_characters_metadata.txt', table_fields)
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
    session.commit()
    logging.info("inserted %s lines", count)


def insert_conversations(session):
    logging.info("inserting conversations ...")

    # Omit conversation_id field since it is automatically generated
    table_fields = [c.name for c in Conversation.__table__.columns
                    if c.name != 'conversation_id']
    data_stream = prepare_data('corpus/movie_conversations.txt', table_fields)
    for conv_id, data in enumerate(data_stream, 1):
        conv_data, line_ids = data

        conversation = Conversation(conversation_id=conv_id, **conv_data)
        session.add(conversation)
        # conv_id = conversation.conversation_id
        # print(conv_id)

        for l_id in line_ids:
            title_genre = ConversationLines(
                conversation_id=conv_id,
                line_id=l_id)
            session.add(title_genre)

    session.commit()
    logging.info("inserted %s conversations", conv_id)


def main():
    directory = os.path.abspath(os.path.dirname(__file__))
    database_uri = 'sqlite:///' + os.path.join(directory, 'movie_dialogs.db')

    engine = create_engine(database_uri)

    Session = sessionmaker(bind=engine)
    session = Session()

    Base.metadata.create_all(engine)

    insert_genres(session)
    insert_titles(session)
    insert_characters(session)
    insert_lines(session)
    insert_conversations(session)


if __name__ == '__main__':
    logging.basicConfig(format='[%(levelname)s] %(message)s',
                        level=logging.INFO)

    main()
