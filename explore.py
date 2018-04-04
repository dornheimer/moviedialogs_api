import os
import sys
import textwrap
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from mappings import Conversation, Character, Movie, Genre
from create_db import database_uri


def print_conversation(session, conversation_id, show_info=True):
    conv = session.query(Conversation).get(conversation_id)
    first_char = session.query(Character).get(conv.first_char_id)
    second_char = session.query(Character).get(conv.second_char_id)
    lines = conv.lines

    if show_info:
        print(f"{conversation_id} - {conv.movie} ({conv.movie.id})")
        print(f"{first_char}, {second_char} ({len(lines)} lines)")
        print("*" * 20)

    for line in reversed(lines):
        s = f"{line.id} {line.character_name}: {line}"
        s = s.encode('ascii', 'ignore').decode('utf-8')
        for line_num, wrapped_line in enumerate(textwrap.wrap(s)):
            if line_num != 0:
                wrapped_line = "\t" + wrapped_line
            print(wrapped_line)


def print_movie(session, movie_id, show_convs=False, to_file=False):
    movie = session.query(Movie).get(movie_id)
    str_genres = [str(genre) for genre in movie.genres]
    str_characters = [str(char) for char in movie.characters]

    if to_file:
        file_name = str(movie_id) + "_" + "_".join(movie.title.split())
        try:
            f = open(f'conversations/{file_name}.txt', 'w')
        except FileNotFoundError:
            os.mkdir('conversations')
            f = open(f'conversations/{file_name}.txt', 'w')
        sys.stdout = f

    print(f"{movie_id} {movie} [{', '.join(str_genres)}]")
    print(f"Characters: {', '.join(str_characters)}")
    print("# Conversations: {}, # Lines: {}".format(
        len(movie.conversations), len(movie.lines)))

    if show_convs:
        convs = [str(conv.id) for conv in movie.conversations]
        print(", ".join(convs))

    if to_file:
        print("")
        for conv in movie.conversations:
            print("CONV_ID", conv.id)
            print_conversation(session, conv.id, show_info=False)
            print("*" * 20)
        sys.stdout = sys.__stdout__
        f.close()


def print_character(session, character_id, show_convs=False, show_lines=False):
    char = session.query(Character).get(character_id)

    print(f"{char} ({character_id}) - {char.movie} ({char.movie.id})")
    print(f"Gender: {char.gender}, Credit position: {char.credit_pos}")
    print("# Conversations: {}, # Lines: {}".format(
        len(char.conversations), len(char.lines)))

    if show_convs:
        convs = [str(conv.id) for conv in char.conversations]
        print(", ".join(convs))

    if show_lines:
        lines = [str(line.id) for line in char.lines]
        print(", ".join(lines))


def print_genre(session, genre_id, show_movies=False):
    genre = session.query(Genre).get(genre_id)

    print(f"{genre_id} {genre}")
    print(f"# Movies: {len(genre.movies)}")

    if show_movies:
        movies = [str(movie.id) for movie in genre.movies]
        print(", ".join(movies))


def main():
    engine = create_engine(database_uri)

    Session = sessionmaker(bind=engine)
    session = Session()

    print_conversation(session, 500)
    print_movie(session, 'm56', show_convs=True, to_file=True)
    print_character(session, 'u35', show_convs=True, show_lines=True)
    print_genre(session, '3', show_movies=True)


if __name__ == '__main__':
    main()
