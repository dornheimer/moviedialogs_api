from sqlalchemy import (Table, Column, Float, Integer, String, ForeignKey,
                        ForeignKeyConstraint, Index)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

movies_genres = Table('movie_genres', Base.metadata,
                      Column('movie_id', String, ForeignKey('movies.id')),
                      Column('genre_id', Integer, ForeignKey('genres.id'))
                      )


class Movie(Base):
    __tablename__ = 'movies'

    id = Column(String, primary_key=True)
    title = Column(String)
    year = Column(String)
    imdb_rating = Column(Float)
    num_imdb_votes = Column(Integer)

    __table_args__ = (Index('movie_ix', 'id', 'title', unique=True),
                      {})

    genres = relationship('Genre', secondary=movies_genres,
                          back_populates='movies')
    characters = relationship('Character', back_populates='movie')
    lines = relationship('Line', back_populates='movie')
    conversations = relationship('Conversation', back_populates='movie')

    def __repr__(self):
        return ('<Movie {!r}>').format(self.title)

    def __str__(self):
        return self.title


class Genre(Base):
    __tablename__ = 'genres'

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)

    movies = relationship('Movie', secondary=movies_genres,
                          back_populates='genres')

    def __repr__(self):
        return ('<Genre {!r}>').format(self.name)

    def __str__(self):
        return self.name


convs_chars = Table('convs_chars', Base.metadata,
                    Column('conversation_id', Integer,
                           ForeignKey('conversations.id')),
                    Column('character_id', String, ForeignKey('characters.id'))
                    )


class Character(Base):
    __tablename__ = 'characters'

    id = Column(String, primary_key=True)
    name = Column(String)
    movie_id = Column(String)
    movie_title = Column(String)
    gender = Column(String, nullable=True)
    credit_pos = Column(Integer, nullable=True)

    __table_args__ = (ForeignKeyConstraint([movie_id, movie_title],
                                           [Movie.id, Movie.title]),
                      Index('character_ix', 'id', 'name', unique=True),
                      {})

    movie = relationship('Movie', back_populates='characters')
    lines = relationship('Line', back_populates='character')
    conversations = relationship('Conversation', secondary=convs_chars,
                                 back_populates='characters')

    def __repr__(self):
        return ('<Character {!r}>').format(self.name)

    def __str__(self):
        return self.name


class Line(Base):
    __tablename__ = 'lines'

    id = Column(String, primary_key=True, index=True)
    character_id = Column(String)
    movie_id = Column(String, ForeignKey('movies.id'))
    character_name = Column(String)
    text = Column(String)
    conversation_id = Column(Integer, ForeignKey('conversations.id'))

    __table_args__ = (ForeignKeyConstraint([character_id, character_name],
                                           [Character.id, Character.name]),
                      {})

    movie = relationship('Movie', back_populates='lines')
    conversation = relationship('Conversation', back_populates='lines')
    character = relationship('Character', back_populates='lines')

    def __repr__(self):
        return ('<Line {!r}>').format(self.id)

    def __str__(self):
        return self.text


class Conversation(Base):
    __tablename__ = 'conversations'

    id = Column(Integer, primary_key=True)
    first_char_id = Column(String, ForeignKey('characters.id'))
    second_char_id = Column(String, ForeignKey('characters.id'))
    movie_id = Column(String, ForeignKey('movies.id'))

    movie = relationship('Movie', back_populates='conversations')
    lines = relationship('Line', back_populates='conversation')
    characters = relationship('Character', secondary=convs_chars,
                              back_populates='conversations')

    def __repr__(self):
        return ('<Conversation {!r} ({}, {})>').format(
            self.movie_id, self.first_char_id, self.second_char_id)
