from sqlalchemy import (
    Column,
    Float,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    Table,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.schema import MetaData

metadata = MetaData(
    naming_convention={
        'ix': 'ix_%(column_0_label)s',
        'uq': 'uq_%(table_name)s_%(column_0_name)s',
        'ck': 'ck_%(table_name)s_%(constraint_name)s',
        'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
        'pk': 'pk_%(table_name)s'
    }
)
Base = declarative_base(metadata=metadata)

convs_chars = Table(
    'convs_chars',
    Base.metadata,
    Column(
        'conversation_id',
        Integer,
        ForeignKey('conversations.id', onupdate='CASCADE', ondelete='SET NULL')
    ),
    Column(
        'character_id',
        String,
        ForeignKey('characters.id', onupdate='CASCADE', ondelete='SET NULL')
    )
)

movies_genres = Table(
    'movie_genres',
    Base.metadata,
    Column('movie_id', String, ForeignKey('movies.id')),
    Column('genre_id', Integer, ForeignKey('genres.id'))
)


class Movie(Base):
    __tablename__ = 'movies'
    id = Column(String, primary_key=True)

    imdb_rating = Column(Float)
    num_imdb_votes = Column(Integer)
    title = Column(String)
    year = Column(String)

    __table_args__ = (Index('ix_movies_id_movie_title', 'id', 'title', unique=True), {})

    characters = relationship('Character', back_populates='movie')
    conversations = relationship('Conversation', back_populates='movie')
    genres = relationship('Genre', secondary=movies_genres, back_populates='movies')
    lines = relationship('Line', back_populates='movie')

    file_mapping = [
        'id',
        'title',
        'year',
        'imdb_rating',
        'num_imdb_votes'
    ]

    def __repr__(self):
        return ('<Movie {!r}>').format(self.title)


class Genre(Base):
    __tablename__ = 'genres'
    id = Column(Integer, primary_key=True)

    name = Column(String)

    movies = relationship('Movie', secondary=movies_genres, back_populates='genres')

    def __repr__(self):
        return ('<Genre {!r}>').format(self.name)


class Character(Base):
    __tablename__ = 'characters'
    id = Column(String, primary_key=True)

    credit_pos = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    movie_id = Column(String)
    movie_title = Column(String)
    name = Column(String)

    __table_args__ = (
        ForeignKeyConstraint([movie_id, movie_title], [Movie.id, Movie.title]),
        Index('ix_character_id_character_name', 'id', 'name', unique=True),
        {}
    )

    conversations = relationship(
        'Conversation',
        secondary=convs_chars,
        back_populates='characters'
    )
    lines = relationship('Line', back_populates='character')
    movie = relationship('Movie', back_populates='characters')

    file_mapping = [
        'id',
        'name',
        'movie_id',
        'movie_title',
        'gender',
        'credit_pos'
    ]

    def __repr__(self):
        return ('<Character {!r}>').format(self.name)


class Line(Base):
    __tablename__ = 'lines'
    id = Column(String, primary_key=True)

    character_id = Column(String)
    character_name = Column(String)
    conversation_id = Column(Integer, ForeignKey('conversations.id'))
    movie_id = Column(String, ForeignKey('movies.id'))
    text = Column(String)

    __table_args__ = (
        ForeignKeyConstraint([character_id, character_name], [Character.id, Character.name]),
        {}
    )

    character = relationship('Character', back_populates='lines')
    conversation = relationship('Conversation', back_populates='lines')
    movie = relationship('Movie', back_populates='lines')

    file_mapping = [
        'id',
        'character_id',
        'movie_id',
        'character_name',
        'text'
    ]

    def __repr__(self):
        return ('<Line {!r}>').format(self.id)


class Conversation(Base):
    __tablename__ = 'conversations'
    id = Column(Integer, primary_key=True)

    first_char_id = Column(
        String,
        ForeignKey('characters.id', onupdate='CASCADE', ondelete='SET NULL')
    )
    second_char_id = Column(
        String,
        ForeignKey('characters.id', onupdate='CASCADE', ondelete='SET NULL')
    )
    movie_id = Column(String, ForeignKey('movies.id'))

    characters = relationship('Character', secondary=convs_chars, back_populates='conversations')
    lines = relationship('Line', back_populates='conversation')
    movie = relationship('Movie', back_populates='conversations')

    file_mapping = [
        'first_char_id',
        'second_char_id',
        'movie_id'
    ]

    def __repr__(self):
        return ('<Conversation {!r} ({}, {})>').format(
            self.movie_id,
            self.first_char_id,
            self.second_char_id
        )
