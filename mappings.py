from sqlalchemy import Column, Float, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Movie(Base):
    __tablename__ = 'movies'

    id = Column(String, primary_key=True)
    title = Column(String)
    year = Column(Integer)
    imdb_rating = Column(Float)
    num_imdb_votes = Column(Integer)
    genres = Column(String)

    #characters = relationship('Character', backref='movie')
    lines = relationship('Line', backref='movie')
    conversations = relationship('Conversation', backref='movie')
    genres = relationship('MovieGenres', backref='movie')

    def __repr__(self):
        return ('<Movie {!r}>').format(self.title)


class Genre(Base):
    __tablename__ = 'genres'

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)

    def __repr__(self):
        return ('<Genre {!r}>').format(self.name)


class MovieGenres(Base):
    __tablename__ = 'movie_genres'

    movie_id = Column(String, ForeignKey('movies.id'), primary_key=True)
    genre_id = Column(String, ForeignKey('genres.id'), primary_key=True)


class Character(Base):
    __tablename__ = 'characters'

    id = Column(String, primary_key=True)
    name = Column(String)
    movie_id = Column(String, ForeignKey('movies.id'))
    movie_title = Column(String, ForeignKey('movies.title'))
    gender = Column(String, nullable=True)
    credit_pos = Column(Integer, nullable=True)

    #lines = relationship('Line')
    character_movie_id = relationship('Movie', foreign_keys='Character.movie_id')
    character_movie_title = relationship('Movie', foreign_keys='Character.movie_title')

    def __repr__(self):
        return ('<Character {!r}>').format(self.name)


class Line(Base):
    __tablename__ = 'lines'

    id = Column(String, primary_key=True, index=True)
    character_id = Column(String, ForeignKey('characters.id'))
    movie_id = Column(String, ForeignKey('movies.id'))
    character_name = Column(String, ForeignKey('characters.name'))
    text = Column(String)

    conversations = relationship('ConversationLines', backref='lines')
    line_character_id = relationship('Character',
                                     foreign_keys='Line.character_id')
    line_character_name = relationship('Character',
                                       foreign_keys='Line.character_name')

    def __repr__(self):
        return ('<Line {!r}>').format(self.line_id)


class Conversation(Base):
    __tablename__ = 'conversations'

    id = Column(Integer, primary_key=True)
    first_char_id = Column(String, ForeignKey('characters.id'))
    second_char_id = Column(String, ForeignKey('characters.id'))
    movie_id = Column(String, ForeignKey('movies.id'))

    lines = relationship('ConversationLines', backref='conversations')

    def __repr__(self):
        return ('<Conversation {!r} ({}, {})>').format(
            self.movie_id, self.first_char_id, self.second_char_id)


class ConversationLines(Base):
    __tablename__ = 'conversation_lines'

    conversation_id = Column(Integer, ForeignKey('conversations.id'),
                             primary_key=True)
    line_id = Column(String, ForeignKey('lines.id'), primary_key=True)
