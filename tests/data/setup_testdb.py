import json

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import TestingConfig
from db.models import (
    Base,
    Character,
    Conversation,
    Genre,
    Line,
    Movie,
)
from tests.data import TESTDATA_PATH


def get_data(json_file):
    with open(json_file) as f:
        return json.load(f)


def insert_movie_and_genres(session, m_dict):
    movie = Movie(**m_dict['movie_data'])

    for g in m_dict['movie_genres']:
        g_obj = session.query(Genre).get(g['id'])
        if g_obj is None:
            g_obj = Genre(**g)
            session.add(g_obj)
        movie.genres.append(g_obj)
    session.add(movie)


def insert_characters(session, m_dict):
    for char_data in m_dict['movie_characters']:
        session.add(Character(**char_data))


def insert_conversations(session, m_dict):
    characters = {}
    for conv_data in m_dict['movie_conversations']:
        conv = Conversation(**conv_data)

        for char_id in (conv.first_char_id, conv.second_char_id):
            char = characters.get(char_id, None)
            if char is None:
                char = session.query(Character).get(char_id)
                characters[char_id] = char

            conv.characters.append(char)

        session.add(conv)


def insert_lines(session, m_dict):
    for l_data in m_dict['movie_lines']:
        line = Line(**l_data)
        conv = session.query(Conversation).get(l_data['conversation_id'])
        conv.lines.append(line)


def main():
    engine = create_engine(TestingConfig.SQLALCHEMY_DATABASE_URI)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Create database tables
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    test_data = get_data(TESTDATA_PATH)
    for m_dict in test_data.values():
        insert_movie_and_genres(session, m_dict)
        insert_characters(session, m_dict)
        insert_conversations(session, m_dict)
        insert_lines(session, m_dict)
    session.commit()


if __name__ == '__main__':
    main()
