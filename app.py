
import os
import re
import requests

from dotenv import load_dotenv
from flask import Flask, request
from flask_cors import CORS
from sqlalchemy import or_

from config import Config
from extensions import db, migrate, jwt

from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)

from models import (Movie,
    Director,
    Genre,
    User,
    UserCollection,
    ThirdPartyRating, MovieGenres
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

load_dotenv()


def create_movie_app(testing=False):
    movie_app = Flask(__name__)

    movie_app.config.from_object(Config)
    movie_app.config['TESTING'] = testing

    jwt_secret = os.environ.get("JWT_SECRET_KEY")

    if not jwt_secret:
        raise RuntimeError(
            "JWT_SECRET_KEY is missing from the .env file."
        )

    movie_app.config["JWT_SECRET_KEY"] = jwt_secret

    db.init_app(movie_app)
    jwt.init_app(movie_app)
    migrate.init_app(movie_app, db)

    CORS(
        movie_app,
        resources={r"/*": {"origins": "*"}},
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )

    @movie_app.route('/')
    def home():
        return {
            'message': 'This is the Movie Tracker API!'
        }, 200

    @movie_app.route('/register', methods=['POST'])
    def register():
        data = request.get_json(silent=True)

        if not data:
            return {'message': 'No data provided.'}, 400

        Username = data.get('userName')
        Email = data.get('email')
        Password = data.get('userPassword')

        if not isinstance(Username, str) or not isinstance(Email, str) or not isinstance(Password, str):
            return {
                'message': 'Username, email and password are required.'
            }, 400

        Username = Username.strip()
        Email = Email.strip()

        if not Username or not Email or not Password:
            return {
                'message': 'Username, email and password are required.'
            }, 400

        movie_user = User.query.filter_by(
            userName=Username
        ).first()

        if movie_user:
            return {'message': 'User already exists.'}, 409

        user_email = User.query.filter_by(
            email=Email
        ).first()

        if user_email:
            return {'message': 'Email already exists.'}, 409

        if len(Password) <= 8:
            return {
                'message': 'Password must be more than 8 characters.'
            }, 400

        if not re.search(r'[A-Z]', Password):
            return {
                'message': 'Password must have at least one uppercase letter.'
            }, 400

        if not re.search(r'[^a-zA-Z0-9]', Password):
            return {
                'message': 'Password must have at least one special character.'
            }, 400

        if not re.search(r'[0-9]', Password):
            return {
                'message': 'Password must have at least one number.'
            }, 400

        secured = generate_password_hash(Password)

        newUser = User(
            userName=Username,
            email=Email,
            userPassword=secured
        )

        try:
            db.session.add(newUser)
            db.session.commit()

            return {
                'message': 'User is registered.',
                'user': {
                    'userID': str(newUser.userID),
                    'userName': newUser.userName,
                    'email': newUser.email
                }
            }, 201

        except Exception:
            db.session.rollback()
            movie_app.logger.exception("Registration failed.")

            return {
                'message': 'Registration error.'
            }, 500

    @movie_app.route('/login', methods=['POST'])
    def login():
        data = request.get_json(silent=True)

        if not data:
            return {'message': 'No data provided.'}, 400

        Username = data.get('userName')
        Password = data.get('userPassword')

        if Username is None or Password is None:
            return {
                'message': 'Username and password cannot be None.'
            }, 400

        if not isinstance(Username, str) or not isinstance(Password, str):
            return {
                'message': 'Username and password must be valid text.'
            }, 400

        Username = Username.strip()

        if not Username or not Password:
            return {
                'message': 'Username and password are required.'
            }, 400

        moviePerson = User.query.filter_by(
            userName=Username
        ).first()

        if not moviePerson or not check_password_hash(moviePerson.userPassword, Password
        ):
            return {
                'message': 'Invalid username or password.'
            }, 401

        moviePerson = User.query.filter_by(
            userName=Username
        ).first()

        print("Username received:", repr(Username))
        print("User found:", moviePerson is not None)

        if moviePerson:
            print("Password hash exists:", bool(moviePerson.userPassword))
            print(
                "Password verification:",
                check_password_hash(moviePerson.userPassword, Password)
            )

        access_token = create_access_token(
            identity=str(moviePerson.userID)
        )

        return {
            'message': 'Login successful.',
            'access_token': access_token,
            'moviePerson': {
                'userID': str(moviePerson.userID),
                'userName': moviePerson.userName,
                'email': moviePerson.email
            }
        }, 200

    @movie_app.route('/test-tmdb-api', methods=['GET'])
    def test_tmdb_api():
        tmdb_api_key = os.getenv('TMDB_API_KEY')

        if not tmdb_api_key:
            return {
                'message': 'TMDB API key is not setup.'
            }, 500

        try:
            tmdb_info = requests.get(
                'https://api.themoviedb.org/3/search/movie',
                params={
                    'api_key': tmdb_api_key,
                    'query': 'Titanic',
                    'year': 1997
                },
                timeout=20
            )

            if tmdb_info.status_code != 200:
                return {
                    'message': 'TMDB API request failed.',
                    'status_code': tmdb_info.status_code
                }, 502

            info_results = tmdb_info.json().get('results', [])

            if not info_results:
                return {
                    'message': 'No results found for the given query.'
                }, 404

            movie_info = info_results[0]
            poster_path = movie_info.get('poster_path')

            return {
                'TMDB_ID': movie_info['id'],
                'title': movie_info['title'],
                'releaseYear': movie_info.get('release_date', '')[:4],
                'thumbnailURL': (
                    f'https://image.tmdb.org/t/p/w500{poster_path}'
                    if poster_path else None
                ),
                'externalRater': 'TMDB',
                'ratingValue': movie_info.get('vote_average')
            }, 200

        except requests.RequestException:
            movie_app.logger.exception("TMDB request failed.")

            return {
                'message': 'Error connecting to TMDB.'
            }, 502

    @movie_app.route('/test-db')
    def test_db():
        genres = db.session.query(Genre).all()

        return {
            'message': 'Database query successful!',
            'genre_count': len(genres),
            'genres': [genre.genre for genre in genres]
        }, 200

   
    
    @movie_app.route('/search', methods=['GET'])
    def search_movies():
        movie_request = request.args.get('query', '').strip()
        search_type = request.args.get('type', 'title').strip().lower()

        if not movie_request:
            return {
                'message': 'Enter a movie title, genre or director name.'
            }, 400

        if search_type not in ['title', 'genre', 'director']:
            return {
                'message': 'Invalid search type. Use title, genre or director.'
            }, 400

        try:
            local_query = db.session.query(Movie)

            if search_type == 'title':
                local_query = local_query.filter(
                    Movie.title.ilike(f'%{movie_request}%')
                )

            elif search_type == 'director':
                local_query = (
                    local_query
                    .join(Movie.directors)
                    .filter(
                        Director.directorName.ilike(
                            f'%{movie_request}%'
                        )
                    )
                )

            elif search_type == 'genre':
                local_query = (
                    local_query
                    .join(Movie.genres)
                    .filter(
                        Genre.genre.ilike(f'%{movie_request}%')
                    )
                )

            movies = local_query.distinct().all()

            movie_list = []

            for movie in movies:
                movie_list.append({
                    'movieID': str(movie.movieID),
                    'TMDB_ID': movie.TMDB_ID,
                    'thumbnailURL': movie.thumbnailURL,
                    'title': movie.title,
                    'releaseYear': movie.releaseYear,
                    'synopsis': movie.synopsis,
                    'directors': [
                        director.directorName
                        for director in movie.directors
                    ],
                    'genres': [
                        genre.genre
                        for genre in movie.genres
                    ],
                    'thirdPartyRatings': [
                        {
                            'externalRater': rating.externalRater,
                            'ratingValue': rating.ratingValue
                        }
                        for rating in movie.thirdPartyRatings
                    ]
                })

            if movie_list:
                return {
                    'source': 'database',
                    'search_type': search_type,
                    'movie_request': movie_request,
                    'result_count': len(movie_list),
                    'movies': movie_list
                }, 200

            tmdb_api_key = os.getenv('TMDB_API_KEY')

            if not tmdb_api_key:
                return {
                    'message': 'TMDB API key is not setup.'
                }, 500

            tmdb_movies = []

            if search_type == 'title':
                tmdb_response = requests.get(
                    'https://api.themoviedb.org/3/search/movie',
                    params={
                        'api_key': tmdb_api_key,
                        'query': movie_request
                    },
                    timeout=20
                )

                tmdb_response.raise_for_status()
                tmdb_movies = tmdb_response.json().get('results', [])

            elif search_type == 'director':
                person_response = requests.get(
                    'https://api.themoviedb.org/3/search/person',
                    params={
                        'api_key': tmdb_api_key,
                        'query': movie_request
                    },
                    timeout=20
                )

                person_response.raise_for_status()
                people = person_response.json().get('results', [])

                if not people:
                    return {
                        'source': 'TMDB',
                        'search_type': search_type,
                        'movie_request': movie_request,
                        'result_count': 0,
                        'movies': [],
                        'message': 'Director not found on TMDB.'
                    }, 200

                director = people[0]

                credits_response = requests.get(
                    f"https://api.themoviedb.org/3/person/{director['id']}/movie_credits",
                    params={
                        'api_key': tmdb_api_key
                    },
                    timeout=20
                )

                credits_response.raise_for_status()
                credits = credits_response.json()

                for crew_member in credits.get('crew', []):
                    if crew_member.get('job') == 'Director':
                        tmdb_movies.append(crew_member)

            elif search_type == 'genre':
                genre_response = requests.get(
                    'https://api.themoviedb.org/3/genre/movie/list',
                    params={
                        'api_key': tmdb_api_key
                    },
                    timeout=20
                )

                genre_response.raise_for_status()

                available_genres = genre_response.json().get(
                    'genres', []
                )

                matching_genres = [
                    genre for genre in available_genres
                    if genre_request_matches(
                        genre.get('name', ''),
                        movie_request
                    )
                ]

                if not matching_genres:
                    return {
                        'source': 'TMDB',
                        'search_type': search_type,
                        'movie_request': movie_request,
                        'result_count': 0,
                        'movies': [],
                        'message': 'Genre not found on TMDB.'
                    }, 200

                genre_id = matching_genres[0]['id']

                discover_response = requests.get(
                    'https://api.themoviedb.org/3/discover/movie',
                    params={
                        'api_key': tmdb_api_key,
                        'with_genres': genre_id,
                        'sort_by': 'popularity.desc',
                        'page': 1
                    },
                    timeout=20
                )

                discover_response.raise_for_status()

                tmdb_movies = discover_response.json().get(
                    'results', []
                )

            external_movies = []

            for movie in tmdb_movies:
                poster_path = movie.get('poster_path')

                thumbnail_url = (
                    f"https://image.tmdb.org/t/p/w500{poster_path}"
                    if poster_path else ''
                )

                release_date = movie.get('release_date', '')

                release_year = (
                    int(release_date[:4])
                    if release_date and release_date[:4].isdigit()
                    else None
                )

                external_movies.append({
                    'TMDB_ID': movie.get('id'),
                    'title': movie.get('title'),
                    'releaseYear': release_year,
                    'synopsis': movie.get('overview'),
                    'thumbnailURL': thumbnail_url,
                    'ratingValue': movie.get('vote_average')
                })

            return {
                'source': 'TMDB',
                'search_type': search_type,
                'movie_request': movie_request,
                'result_count': len(external_movies),
                'movies': external_movies
            }, 200

        except requests.RequestException:
            movie_app.logger.exception('TMDB search failed.')

            return {
                'message': 'Error connecting to TMDB.'
            }, 502

        except Exception:
            db.session.rollback()
            movie_app.logger.exception('Movie search failed.')

            return {
                'message': 'An error occurred while searching for movies.'
            }, 500


    def genre_request_matches(genre_name, search_request):
        return genre_name.strip().lower() == search_request.strip().lower()


    @movie_app.route('/add-to-movie-collections', methods=['POST'])
    @jwt_required()
    def add_to_movie_collections():
        data = request.get_json(silent=True)

        if not data:
            return {'message': 'No data provided.'}, 400

        movie_id = data.get('movieID')

        if not movie_id:
            return {'message': 'movieID is required.'}, 400

        user_id = get_jwt_identity()

        user = db.session.get(User, user_id)
        movie = db.session.get(Movie, movie_id)

        if not user:
            return {'message': 'User not found.'}, 404

        if not movie:
            return {'message': 'Movie not found.'}, 404

        existing_entry = (
            db.session.query(UserCollection)
            .filter_by(
                userID=user.userID,
                movieID=movie.movieID
            )
            .first()
        )

        if existing_entry:
            return {
                'message': 'This movie is already in your collection.'
            }, 409

        new_collection_entry = UserCollection(
            userID=user.userID,
            movieID=movie.movieID
        )

        try:
            db.session.add(new_collection_entry)
            db.session.commit()

            return {
                'message': 'Movie added to your collection successfully.',
                'collectionID': str(new_collection_entry.collectionID),
                'userID': str(user.userID),
                'movieID': str(movie.movieID),
                'title': movie.title
            }, 201

        except Exception:
            db.session.rollback()
            movie_app.logger.exception("Could not add movie to collection.")

            return {
                'message': 'Failed to add movie to your collection.'
            }, 500

    @movie_app.route('/get-user-collections/<user_id>', methods=['GET'])
    @jwt_required()
    def get_user_collections(user_id):
        authenticated_user_id = get_jwt_identity()

        if str(user_id) != str(authenticated_user_id):
            return {
                'message': 'You are not authorized to view this collection.'
            }, 403

        user = db.session.get(User, authenticated_user_id)

        if not user:
            return {'message': 'User not found.'}, 404

        collections = UserCollection.query.filter_by(
            userID=user.userID
        ).all()

        collection_list = []

        for collection in collections:
            movie = db.session.get(Movie, collection.movieID)

            if not movie:
                continue

            collection_list.append({
                'collectionID': str(collection.collectionID),
                'movieID': str(movie.movieID),
                'title': movie.title,
                'releaseYear': movie.releaseYear,
                'synopsis': movie.synopsis,
                'thumbnailURL': movie.thumbnailURL,
                'directors': [
                    director.directorName
                    for director in movie.directors
                ],
                'genres': [
                    genre.genre
                    for genre in movie.genres
                ],
                'thirdPartyRatings': [
                    {
                        'externalRater': rating.externalRater,
                        'ratingValue': rating.ratingValue
                    }
                    for rating in movie.thirdPartyRatings
                ],
                'rating': (
                    float(collection.rating)
                    if collection.rating is not None else None
                )
            })

        return {
            'userID': str(user.userID),
            'collection_count': len(collection_list),
            'collections': collection_list
        }, 200

    @movie_app.route('/add-rate-movie/<collection_id>', methods=['POST'])
    @jwt_required()
    def Add_Movierating(collection_id):
        data = request.get_json(silent=True)

        if not data:
            return {'message': 'No data available.'}, 400

        rating_value = data.get('rating')

        if rating_value is None:
            return {'message': 'Rating value is required.'}, 400

        try:
            rating_value = float(rating_value)
        except (ValueError, TypeError):
            return {
                'message': 'Rating value must be a number.'
            }, 400

        if not (0 <= rating_value <= 10):
            return {
                'message': 'Rating value must be between 0 and 10.'
            }, 400

        collection_entry = db.session.get(
            UserCollection,
            collection_id
        )

        if not collection_entry:
            return {'message': 'Collection entry not found.'}, 404

        authenticated_user_id = get_jwt_identity()

        if str(collection_entry.userID) != str(authenticated_user_id):
            return {
                'message': 'You are not authorized to rate this movie.'
            }, 403

        if collection_entry.rating is not None:
            return {
                'message': 'This movie has already been rated.'
            }, 409

        try:
            collection_entry.rating = rating_value
            db.session.commit()

            return {
                'message': 'Rating added successfully.',
                'collectionID': str(collection_entry.collectionID),
                'rating': float(collection_entry.rating)
            }, 201

        except Exception:
            db.session.rollback()
            movie_app.logger.exception("Failed to add movie rating.")

            return {
                'message': 'Failed to add movie rating.'
            }, 500

    @movie_app.route('/update-rate-movie/<collection_id>', methods=['PUT'])
    @jwt_required()
    def Update_Movierating(collection_id):
        data = request.get_json(silent=True)

        if not data:
            return {'message': 'No data available.'}, 400

        rating_value = data.get('rating')

        if rating_value is None:
            return {'message': 'Rating value is required.'}, 400

        try:
            rating_value = float(rating_value)
        except (ValueError, TypeError):
            return {
                'message': 'Rating value must be a number.'
            }, 400

        if not (0 <= rating_value <= 10):
            return {
                'message': 'Rating value must be between 0 and 10.'
            }, 400

        collection_entry = db.session.get(
            UserCollection,
            collection_id
        )

        if not collection_entry:
            return {'message': 'Collection entry not found.'}, 404

        authenticated_user_id = get_jwt_identity()

        if str(collection_entry.userID) != str(authenticated_user_id):
            return {
                'message': 'You are not authorized to update this rating.'
            }, 403

        if collection_entry.rating is None:
            return {
                'message': 'No existing rating found. Use the add-rating endpoint first.'
            }, 400

        try:
            collection_entry.rating = rating_value
            db.session.commit()

            return {
                'message': 'Rating updated successfully.',
                'collectionID': str(collection_entry.collectionID),
                'rating': float(collection_entry.rating)
            }, 200

        except Exception:
            db.session.rollback()
            movie_app.logger.exception("Failed to update movie rating.")

            return {
                'message': 'Failed to update movie rating.'
            }, 500

    @movie_app.route('/delete-movie/<collection_id>', methods=['DELETE'])
    @jwt_required()
    def delete_movie_from_collection(collection_id):
        collection_entry = db.session.get(
            UserCollection,
            collection_id
        )

        if not collection_entry:
            return {'message': 'Collection entry not found.'}, 404

        authenticated_user_id = get_jwt_identity()

        if str(collection_entry.userID) != str(authenticated_user_id):
            return {
                'message': 'You are not authorized to remove this movie.'
            }, 403

        try:
            db.session.delete(collection_entry)
            db.session.commit()

            return {
                'message': 'Movie removed from your collection successfully.'
            }, 200

        except Exception:
            db.session.rollback()
            movie_app.logger.exception("Failed to remove movie.")

            return {
                'message': 'Failed to remove movie from your collection.'
            }, 500

   
    @movie_app.route('/add-movie', methods=['POST'])
    def add_movie_to_collection():
        data = request.get_json(silent=True)

        if not data or not data.get('TMDB_ID'):
            return {
                'message': 'TMDB movie ID is required.'
            }, 400

        tmdb_movie_id = data['TMDB_ID']
        tmdb_api_key = os.getenv('TMDB_API_KEY')

        if not tmdb_api_key:
            return {
                'message': 'TMDB API key is not setup.'
            }, 500

        try:
            # Retrieve the exact movie selected by the user.
            tmdb_info = requests.get(
                f'https://api.themoviedb.org/3/movie/{tmdb_movie_id}',
                params={'api_key': tmdb_api_key},
                timeout=20
            )

            if tmdb_info.status_code == 404:
                return {
                    'message': 'Movie not found on TMDB.'
                }, 404

            if tmdb_info.status_code != 200:
                return {
                    'message': 'TMDB API request failed.'
                }, 502

            movie_info = tmdb_info.json()

            # Check whether the movie already exists.
            this_movie = Movie.query.filter_by(
                TMDB_ID=tmdb_movie_id
            ).first()

            poster_path = movie_info.get('poster_path')

            thumbnail_url = (
                f"https://image.tmdb.org/t/p/w500{poster_path}"
                if poster_path else None
            )

            release_date = movie_info.get('release_date', '')

            release_year = (
                int(release_date[:4])
                if release_date and release_date[:4].isdigit()
                else None
            )

            if this_movie:
                return {
                    'message': 'This movie already exists in the catalogue.',
                    'movieID': str(this_movie.movieID),
                    'TMDB_ID': this_movie.TMDB_ID,
                    'title': this_movie.title
                }, 200

            # Create the movie record.
            this_movie = Movie(
                TMDB_ID=tmdb_movie_id,
                title=movie_info['title'],
                releaseYear=release_year,
                synopsis=movie_info.get('overview'),
                thumbnailURL=thumbnail_url
            )

            db.session.add(this_movie)
            db.session.flush()

            # Add the movie's existing genres.
            for tmdb_genre in movie_info.get('genres', []):
                existing_genre = Genre.query.filter(
                    db.func.lower(Genre.genre) ==
                    tmdb_genre['name'].lower()
                ).first()

                if existing_genre:
                    this_movie.genres.append(existing_genre)

            # Add or update the TMDB rating.
            external_rating = movie_info.get('vote_average')

            if external_rating is not None:
                this_rating = ThirdPartyRating(
                    movieID=this_movie.movieID,
                    userID=None,
                    externalRater='TMDB',
                    ratingValue=str(external_rating)
                )

                db.session.add(this_rating)

            db.session.commit()

            return {
                'message': 'Movie added to the catalogue successfully.',
                'movieID': str(this_movie.movieID),
                'TMDB_ID': this_movie.TMDB_ID,
                'title': this_movie.title,
                'releaseYear': this_movie.releaseYear,
                'synopsis': this_movie.synopsis,
                'thumbnailURL': this_movie.thumbnailURL,
                'genres': [
                    genre.genre for genre in this_movie.genres
                ]
            }, 201

        except requests.RequestException:
            db.session.rollback()
            movie_app.logger.exception('Error connecting to TMDB.')

            return {
                'message': 'Error connecting to TMDB.'
            }, 502

        except Exception:
            db.session.rollback()
            movie_app.logger.exception(
                'Failed to save movie information.'
            )

            return {
                'message': 'Failed to save movie information.'
            }, 500

    
    @movie_app.route('/home-movieDisplay', methods=['GET'])
    def home_movie_display():
        Moviegenre = (
            db.session.query(Genre)
            .order_by(Genre.genre)
            .all()
        )

        list_of_genres = []

        for genre in Moviegenre:
            movies = (
                db.session.query(Movie)
                .join(Movie.genres)
                .filter(Genre.genreID == genre.genreID)
                .order_by(Movie.title)
                .all()
            )

            movie_list = []

            for movie in movies:
                movie_list.append({
                    'movieID': str(movie.movieID),
                    'thumbnailURL': movie.thumbnailURL,
                    'title': movie.title,
                    'thirdPartyRatings': [
                        {
                            'externalRater': rating.externalRater,
                            'ratingValue': rating.ratingValue
                        }
                        for rating in movie.thirdPartyRatings
                    ],
                    'directors':[
                        director.directorName for director in movie.directors
                    ]
                })

            list_of_genres.append({
                'genreID': str(genre.genreID),
                'genre': genre.genre,
                'movies': movie_list
            })

        return {
            'genre_count': len(list_of_genres),
            #'movie_count': Movie.query.count(),
            'genres': list_of_genres
        }, 200

    return movie_app


movie_app = create_movie_app()


if __name__ == '__main__':
    movie_app.run(debug=True)
