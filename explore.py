import argparse
from collections import namedtuple
import os
from operator import itemgetter
import sys
import textwrap
import re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from mappings import Conversation, Character, Movie, Genre, Line
from create_db import database_uri


def separator(char='-', length=80):
    def decorate(func):
        def separated(*args, **kwargs):
            rv = func(*args, **kwargs)
            print(char * length)
            return rv
        return separated
    return decorate


def sanitize_html(line_text):
    # Use capture groups to enumerate, and reference group 2 for substitution
    tag_regex = re.compile(r"(<\w+>(.+?)</\w+>)")
    return re.sub(tag_regex, r"\2", line_text)


@separator()
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


@separator()
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

    print("avg lines per conv: {:.2f}".format(stats.lines_per_conv))
    print("avg line length: {:.2f}".format(stats.avg_line_length))
    print("f gender ratio: {:.2f}".format(stats.f_gender_ratio))
    print("chars_avg_lines_per_conv: {:.2f}".format(
        stats.chars_avg_lines_per_conv))
    print("chars_avg_line_length: {:.2f}".format(stats.chars_avg_line_length))

    if show_convs:
        convs = [str(conv.id) for conv in movie.conversations]
        print(", ".join(convs))

    if to_file:
        print("")
        for conv in movie.conversations:
            print("CONV_ID", conv.id)
            print_conversation(session, conv.id, show_info=False)
        print("-" * 80)
        sys.stdout = sys.__stdout__
        f.close()


@separator()
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


@separator()
def print_genre(session, genre_id, show_movies=False):
    genre = session.query(Genre).get(genre_id)

    print(f"{genre_id} {genre}")
    print(f"# Movies: {len(genre.movies)}")

    if show_movies:
        movies = [str(movie.id) for movie in genre.movies]
        print(", ".join(movies))


def print_line(line):
        line_text = line.text
        line_text = line_text.encode('ascii', 'ignore').decode('utf-8')
        line_text = sanitize_html(line_text)
        s = f"{line.id} {line.character_name}: {line_text}"
        for line_num, wrapped_line in enumerate(textwrap.wrap(s)):
            if line_num != 0:
                wrapped_line = "\t" + wrapped_line
            print(wrapped_line)


def avg(numbers):
    return sum(numbers) / len(numbers)


def character_stats(char):
    lines_per_conv = len(char.lines) / len(char.conversations)
    avg_line_length = avg([len(sanitize_html(l.text)) for l in char.lines])

    return lines_per_conv, avg_line_length


MovieStats = namedtuple(
    'MovieStats',
    ['lines_per_conv', 'avg_line_length', 'f_gender_ratio',
     'chars_avg_lines_per_conv', 'chars_avg_line_length']
     )


def movie_stats(movie):
    lines_per_conv = len(movie.lines) / len(movie.conversations)
    avg_line_length = avg([len(sanitize_html(l.text)) for l in movie.lines])

    chars_stats = [character_stats(char) for char in movie.characters]
    chars_avg_lines_per_conv = avg(list(map(itemgetter(0), chars_stats)))
    chars_avg_line_length = avg(list(map(itemgetter(1), chars_stats)))

    genders = [char.gender for char in movie.characters
               if char.gender in ('f', 'm')]
    f_gender_ratio = genders.count('f') / len(genders)

    return MovieStats(lines_per_conv, avg_line_length, f_gender_ratio,
                      chars_avg_lines_per_conv, chars_avg_line_length)


def conversation_stats(conv):
    avg_line_length = avg([len(sanitize_html(l.text)) for l in conv.lines])

    return avg_line_length,


def parse_commandline():
    parser = argparse.ArgumentParser()

    parser.add_argument('--conversation', '-c',
                        metavar='<conversation_id>',
                        dest='conv_id',
                        nargs='+',
                        type=int)

    parser.add_argument('--genre', '-g',
                        metavar='<genre_id>',
                        dest='genre_id',
                        nargs='+',
                        type=int)

    parser.add_argument('--character', '-k',
                        metavar='<character_id>',
                        dest='char_id',
                        nargs='+',)

    parser.add_argument('--movie', '-m',
                        metavar='<movie_id>',
                        dest='movie_id',
                        nargs='+',)

    parser.add_argument('--line', '-l',
                        metavar='<line_id>',
                        dest='line_id',
                        nargs='+',)

    parser.add_argument('--to-file',
                        action='store_true')

    parser.add_argument('--range', '-r',
                        type=int,
                        default=1)

    return parser.parse_args()


def main(args):
    engine = create_engine(database_uri)

    Session = sessionmaker(bind=engine)
    session = Session()

    if args.conv_id:
        if len(args.conv_id) > 1:
            for c_id in args.conv_id:
                print_conversation(session, c_id)
        else:
            start_id = args.conv_id[0]
            stop_id = start_id + args.range
            for c in range(start_id, stop_id):
                print_conversation(session, c)

    if args.movie_id:
        if len(args.movie_id) > 1:
            for m_id in args.movie_id:
                print_movie(session, m_id, show_convs=False,
                            to_file=args.to_file)
        else:
            start_id = args.movie_id[0]
            start_id = int(start_id[1:])  # Get integer component of id
            stop_id = start_id + args.range
            for m in range(start_id, stop_id):
                m_id = f"m{m}"
                print_movie(session, m_id, show_convs=False,
                            to_file=args.to_file)

    if args.char_id:
        if len(args.char_id) > 1:
            for c_id in args.char_id:
                print_character(session, c_id, show_convs=False)
        else:
            start_id = args.char_id[0]
            start_id = int(start_id[1:])
            stop_id = start_id + args.range
            for c in range(start_id, stop_id):
                c_id = f"u{c}"
                print_character(session, c_id, show_convs=False)

    if args.genre_id:
        if len(args.genre_id) > 1:
            for g_id in args.genre_id:
                print_genre(session, g_id, show_movies=True)
        else:
            start_id = args.genre_id[0]
            stop_id = start_id + args.range
            for g_id in range(start_id, stop_id):
                print_genre(session, g_id, show_movies=True)

    if args.line_id:
        if len(args.line_id) > 1:
            for l_id in args.line_id:
                line = session.query(Line).get(l_id)
                print_line(line)
                print("-" * 80)
        else:
            start_id = args.line_id[0]
            start_id = int(start_id[1:])
            stop_id = start_id + args.range
            for l in range(start_id, stop_id):
                l_id = f"L{l}"
                line = session.query(Line).get(l_id)
                try:
                    print_line(line)
                except AttributeError:
                    print("ERROR: Line does not exist")
                print("-" * 80)


if __name__ == '__main__':
    args = parse_commandline()
    main(args)
