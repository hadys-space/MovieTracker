
from sqlalchemy import text
from flask import Flask
from config import Config
from extensions import db, migrate
import models
from models import Genre


def create_movie_app(testing=False):
    movie_app = Flask(__name__)
    movie_app.config.from_object(Config)
    movie_app.config['TESTING'] = testing

    db.init_app(movie_app)
    migrate.init_app(movie_app, db)

        
    '''if not movie_app.config.get("TESTING", False):'''
    if not testing:
        with movie_app.app_context():
            with db.engine.connect() as connection: 
                 result = connection.execute(text("SELECT 1"))
                 print("Database connection successful!:", result.scalar())

    @movie_app.route('/')
    def home():
        return {'message': 'This is the Movie Tracker API!'}

    @movie_app.route('/test-db')
    def test_db():
        genres = db.session.query(Genre).all()

        return {
            'message': 'Database query successful!',
            'genre_count': len(genres),
            'genres': [genre.genre for genre in genres]
        }

    return movie_app


movie_app = create_movie_app()

if __name__ == '__main__':
    movie_app.run(debug=True)
