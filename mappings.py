from sqlalchemy import Column, Float, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Title(Base):
    __tablename__ = 'titles'

    movie_id = Column(String, primary_key=True)
    movie_title = Column(String)
    movie_year = Column(Integer)
    imdb_rating = Column(Float)
    num_imdb_votes = Column(Integer)
    genres = Column(String)

    #characters = relationship('Character', backref='title')
    lines = relationship('Line', backref='title')
    conversations = relationship('Conversation', backref='title')
    genres = relationship('TitleGenres', backref='title')

    def __repr__(self):
        return ('<Title {!r}>').format(self.movie_title)


class Genre(Base):
    __tablename__ = 'genres'

    genre_id = Column(Integer, primary_key=True)
    name = Column(String, index=True)

    def __repr__(self):
        return ('<Genre {!r}>').format(self.name)


class TitleGenres(Base):
    __tablename__ = 'title_genres'

    movie_id = Column(String, ForeignKey('titles.movie_id'), primary_key=True)
    genre_id = Column(String, ForeignKey('genres.genre_id'), primary_key=True)


class Character(Base):
    __tablename__ = 'characters'

    character_id = Column(String, primary_key=True)
    character_name = Column(String)
    movie_id = Column(String, ForeignKey('titles.movie_id'))
    movie_title = Column(String, ForeignKey('titles.movie_title'))
    gender = Column(String, nullable=True)
    credit_pos = Column(Integer, nullable=True)

    #lines = relationship('Line')
    character_movie_id = relationship('Title', foreign_keys='Character.movie_id')
    character_movie_title = relationship('Title', foreign_keys='Character.movie_title')

    def __repr__(self):
        return ('<Character {!r}>').format(self.character_name)


class Line(Base):
    __tablename__ = 'lines'

    line_id = Column(String, primary_key=True, index=True)
    character_id = Column(String, ForeignKey('characters.character_id'))
    movie_id = Column(String, ForeignKey('titles.movie_id'))
    character_name = Column(String, ForeignKey('characters.character_name'))
    text = Column(String)

    conversations = relationship('ConversationLines', backref='lines')
    line_character_id = relationship('Character', foreign_keys='Line.character_id')
    line_character_name = relationship('Character', foreign_keys='Line.character_name')

    def __repr__(self):
        return ('<Line {!r}>').format(self.line_id)


class Conversation(Base):
    __tablename__ = 'conversations'

    conversation_id = Column(Integer, primary_key=True)
    first_char_id = Column(String, ForeignKey('characters.character_id'))
    second_char_id = Column(String, ForeignKey('characters.character_id'))
    movie_id = Column(String, ForeignKey('titles.movie_id'))

    lines = relationship('ConversationLines', backref='conversations')

    def __repr__(self):
        return ('<Conversation {!r} ({}, {})>').format(
            self.movie_id, self.first_char_id, self.second_char_id)


class ConversationLines(Base):
    __tablename__ = 'conversation_lines'

    conversation_id = Column(
Integer, ForeignKey('conversations.conversation_id'), primary_key=True)
    line_id = Column(String, ForeignKey('lines.line_id'), primary_key=True)
