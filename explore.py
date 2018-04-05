import argparse
import os
from operator import itemgetter
import sys
import textwrap
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from mappings import Conversation, Character, Movie, Genre, Line
from create_db import database_uri


def print_conversation(session, conversation_id, show_info=True):
    conv = session.query(Conversation).get(conversation_id)
    first_char = session.query(Character).get(conv.first_char_id)
    second_char = session.query(Character).get(conv.second_char_id)

    if show_info:
        print(f"{conversation_id} - {conv.movie} ({conv.movie.id})")
        print(f"{first_char}, {second_char} ({len(conv)} lines)")
        print("avg line length: {:.2f}".format(*conversation_stats(conv)))
        print("*" * 20)

    for line in reversed(conv.lines):
        print_line(line)


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

    stats = movie_stats(movie)
    print(f"{movie_id} {movie} [{', '.join(str_genres)}]")
    print(f"Characters ({len(movie.characters)}): {', '.join(str_characters)}")
    print("# Conversations: {}, # Lines: {}".format(
        len(movie.conversations), len(movie.lines)))
    print("avg lines per conv: {:.2f}, avg line length: {:.2f}, f gender ratio: {:.2f}".format(
        *stats[:3]))
    print("chars_avg_lines_per_conv: {:.2f}, chars_avg_line_length: {:.2f}".format(
        *stats[3:]))

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
    print("avg lines per conv: {:.2f}, avg line length: {:.2f}".format(
        *character_stats(char)))

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


def print_line(line):
        s = f"{line.id} {line.character_name}: {line}"
        s = s.encode('ascii', 'ignore').decode('utf-8')
        for line_num, wrapped_line in enumerate(textwrap.wrap(s)):
            if line_num != 0:
                wrapped_line = "\t" + wrapped_line
            print(wrapped_line)


def avg(numbers):
    return sum(numbers) / len(numbers)


def character_stats(char):
    lines_per_conv = len(char.lines) / len(char.conversations)
    avg_line_length = avg([len(l) for l in char.lines])

    return lines_per_conv, avg_line_length


def movie_stats(movie):
    lines_per_conv = len(movie.lines) / len(movie.conversations)
    avg_line_length = avg([len(l) for l in movie.lines])

    chars_stats = [character_stats(char) for char in movie.characters]
    chars_avg_lines_per_conv = avg(list(map(itemgetter(0), chars_stats)))
    chars_avg_line_length = avg(list(map(itemgetter(1), chars_stats)))

    genders = [char.gender for char in movie.characters
               if char.gender in ('f', 'm')]
    f_gender_ratio = genders.count('f') / len(genders)

    return lines_per_conv, avg_line_length, f_gender_ratio, chars_avg_lines_per_conv, chars_avg_line_length


def conversation_stats(conv):
    avg_line_length = avg([len(l) for l in conv.lines])

    return avg_line_length,


def parse_commandline():
    parser = argparse.ArgumentParser()
    parser.add_argument('--conversation', '-c', metavar='<conversation_id>')
    parser.add_argument('--genre', '-g', metavar='<genre_id>')
    parser.add_argument('--character', '-k', metavar='<character_id>')
    parser.add_argument('--movie', '-m', metavar='<movie_id>')
    parser.add_argument('--line', '-l', metavar='<line_id>')
    parser.add_argument('--to_file', action='store_true')

    return parser.parse_args()


def main(args):
    engine = create_engine(database_uri)

    Session = sessionmaker(bind=engine)
    session = Session()

    if args.conversation:
        print_conversation(session, args.conversation)
    if args.movie:
        to_file = args.to_file
        print_movie(session, args.movie, show_convs=False, to_file=to_file)
    if args.character:
        print_character(session, args.character, show_convs=True,
                        show_lines=True)
    if args.genre:
        print_genre(session, args.genre, show_movies=True)
    if args.line:
        line = session.query(Line).get(args.line)
        print_line(line)


if __name__ == '__main__':
    args = parse_commandline()
    main(args)
