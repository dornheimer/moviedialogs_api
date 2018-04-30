import os
import sys

from setuptools import setup, find_packages, Command

CORPUS_URL = 'http://www.cs.cornell.edu/~cristian/data/cornell_movie_dialogs_corpus.zip'


class PostInstallCommand(Command):
    """Support setup.py postinstall."""

    description = 'Download the corpus data and create the database.'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        print('Downloading corpus ...')
        os.system(f'wget -nc {CORPUS_URL}')

        print('Extracting ...')
        os.system('unzip -nj {} -d corpus'.format(os.path.basename(CORPUS_URL)))

        print('Creating database tables ...')
        os.system('flask db upgrade')

        print('Inserting data ...')
        os.system('{} -m db.seed'.format(sys.executable))

        sys.exit()

setup(
    version=0.1,
    name='api',
    packages=find_packages(exclude=('tests',)),
    cmdclass={
        'postinstall': PostInstallCommand,
    },
)
