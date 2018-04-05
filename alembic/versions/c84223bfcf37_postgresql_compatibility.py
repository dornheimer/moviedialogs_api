"""postgresql compatibility

Revision ID: c84223bfcf37
Revises: 
Create Date: 2018-03-26 18:59:08.816631

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c84223bfcf37'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('genres',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_genres_name'), 'genres', ['name'], unique=False)
    op.create_table('movies',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('year', sa.String(), nullable=True),
    sa.Column('imdb_rating', sa.Float(), nullable=True),
    sa.Column('num_imdb_votes', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('movie_ix', 'movies', ['id', 'title'], unique=True)
    op.create_table('characters',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('movie_id', sa.String(), nullable=True),
    sa.Column('movie_title', sa.String(), nullable=True),
    sa.Column('gender', sa.String(), nullable=True),
    sa.Column('credit_pos', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['movie_id', 'movie_title'], ['movies.id', 'movies.title'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('character_ix', 'characters', ['id', 'name'], unique=True)
    op.create_table('movie_genres',
    sa.Column('movie_id', sa.String(), nullable=True),
    sa.Column('genre_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['genre_id'], ['genres.id'], ),
    sa.ForeignKeyConstraint(['movie_id'], ['movies.id'], )
    )
    op.create_table('conversations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_char_id', sa.String(), nullable=True),
    sa.Column('second_char_id', sa.String(), nullable=True),
    sa.Column('movie_id', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['first_char_id'], ['characters.id'], ),
    sa.ForeignKeyConstraint(['movie_id'], ['movies.id'], ),
    sa.ForeignKeyConstraint(['second_char_id'], ['characters.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('convs_chars',
    sa.Column('conversation_id', sa.Integer(), nullable=True),
    sa.Column('character_id', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['character_id'], ['characters.id'], ),
    sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], )
    )
    op.create_table('lines',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('character_id', sa.String(), nullable=True),
    sa.Column('movie_id', sa.String(), nullable=True),
    sa.Column('character_name', sa.String(), nullable=True),
    sa.Column('text', sa.String(), nullable=True),
    sa.Column('conversation_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['character_id', 'character_name'], ['characters.id', 'characters.name'], ),
    sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ),
    sa.ForeignKeyConstraint(['movie_id'], ['movies.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_lines_id'), 'lines', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_lines_id'), table_name='lines')
    op.drop_table('lines')
    op.drop_table('convs_chars')
    op.drop_table('conversations')
    op.drop_table('movie_genres')
    op.drop_index('character_ix', table_name='characters')
    op.drop_table('characters')
    op.drop_index('movie_ix', table_name='movies')
    op.drop_table('movies')
    op.drop_index(op.f('ix_genres_name'), table_name='genres')
    op.drop_table('genres')
    # ### end Alembic commands ###