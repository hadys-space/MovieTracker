
from decimal import Decimal

from werkzeug.security import generate_password_hash

from app import create_movie_app
from extensions import db
from models import (
    Director,
    Genre,
    Movie,
    ThirdPartyRating,
    User,
    UserCollection,
)


def data_seeding():
    app = create_movie_app()

    with app.app_context():
        try:
            # 1. GENRES
            genre_names = [
                "Action",
                "Adventure",
                "Animation",
                "Comedy",
                "Crime",
                "Drama",
                "Family",
                "Fantasy",
                "Romance",
                "Science Fiction",
                "Thriller",
                "Horror",
                "Mystery",
            ]

            genres = {}

            for name in genre_names:
                genre = Genre.query.filter_by(genre=name).first()

                if genre is None:
                    genre = Genre(genre=name)
                    db.session.add(genre)

                genres[name] = genre

            db.session.flush()

           
            director_names = [
                "Christopher Nolan",
                "James Cameron",
                "Roger Allers",
                "Rob Minkoff",
                "Lana Wachowski",
                "Lilly Wachowski",
                "James Cameron",
                "Steven Spielberg",
                "Andrew Stanton",
                "John Lasseter",
                "Joss Whedon",
                "Ryan Coogler",
                "Jordan Peele",
                "John Krasinski",
            ]

            directors = {}

            for name in director_names:
                director = Director.query.filter_by(
                    directorName=name
                ).first()

                if director is None:
                    director = Director(directorName=name)
                    db.session.add(director)

                directors[name] = director

            db.session.flush()

            

            movie_data = [
                (
                    27205, "edv5CZvWj09upOsy2Y6IwDhK8bt.jpg", "Inception", 2010,
                    "A thief enters dreams to steal secrets.",
                    ["Christopher Nolan"],
                    ["Action", "Science Fiction", "Thriller"],
                ),
                (
                    155, "qJ2tW6WMUDux911r6m7haRef0WH.jpg", "The Dark Knight", 2008,
                    "Batman faces the criminal mastermind Joker.",
                    ["Christopher Nolan"],
                    ["Action", "Crime", "Drama"],
                ),
                (
                    157336, "gEU2QniE6E77NI6lCU6MxlNBvIx.jpg", "Interstellar", 2014,
                    "Explorers search for a future for humanity.",
                    ["Christopher Nolan"],
                    ["Adventure", "Drama", "Science Fiction"],
                ),
                (
                    597, "9xjZS2rlVxm8SFx8kPC3aIGCOYQ.jpg", "Titanic", 1997,
                    "Two passengers fall in love aboard the Titanic.",
                    ["James Cameron"],
                    ["Drama", "Romance"],
                ),
                (
                    8587, "sKCr78MXSLixwmZ8DyJLrpMsd15.jpg", "The Lion King", 1994,
                    "A young lion learns to accept his destiny.",
                    ["Roger Allers", "Rob Minkoff"],
                    ["Adventure", "Animation", "Family"],
                ),
                (
                    603, "gynBNzwyaHKtXqlEKKLioNkjKgN.jpg", "The Matrix", 1999,
                    "A hacker discovers that reality is simulated.",
                    ["Lana Wachowski", "Lilly Wachowski"],
                    ["Action", "Science Fiction"],
                ),
                (
                    19995, "kyeqWdyUXW608qlYkRqosgbbJyK.jpg", "Avatar", 2009,
                    "A marine explores an alien world called Pandora.",
                    ["James Cameron"],
                    ["Action", "Adventure", "Science Fiction"],
                ),
                (
                    329, "b1xCNnyrPebIc7EWNZIa6jhb1Ww.jpg", "Jurassic Park", 1993,
                    "Scientists encounter dinosaurs at a theme park.",
                    ["Steven Spielberg"],
                    ["Adventure", "Science Fiction", "Thriller"],
                ),
                (
                    862, "uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg", "Toy Story", 1995,
                    "Toys come to life when humans are away.",
                    ["John Lasseter"],
                    ["Animation", "Comedy", "Family"],
                ),
                (
                    24428, "RYMX2wcKCBAr24UyPD7xwmjaTn.jpg", "The Avengers", 2012,
                    "Heroes unite to defend Earth from an invasion.",
                    ["Joss Whedon"],
                    ["Action", "Adventure", "Science Fiction"],
                ),
                (
                    284054, "uxzzxijgPIY7slzFvMotPv8wjKA.jpg", "Black Panther", 2018,
                    "A king protects Wakanda and its people.",
                    ["Ryan Coogler"],
                    ["Action", "Adventure", "Science Fiction"],
                ),
                (
                    419430, "tFXcEccSQMf3lfhfXKSU9iRBpa3.jpg", "Get Out", 2017,
                    "A visit to meet a partner's family becomes disturbing.",
                    ["Jordan Peele"],
                    ["Horror", "Thriller", "Mystery"],
                ),
                (
                    447332, "nAU74GmpUk7t5iklEp3bufwDq4n.jpg", "A Quiet Place", 2018,
                    "A family struggles to survive creatures that hunt by sound.",
                    ["John Krasinski"],
                    ["Horror", "Thriller", "Drama"],
                ),
            ]

            movies = {}

            for (
                tmdb_id,
                thumbnailURL,
                title,
                year,
                synopsis,
                movie_directors,
                movie_genres,
            ) in movie_data:

                movie = Movie.query.filter_by(
                    TMDB_ID=tmdb_id
                ).first()

                if movie is None:
                    movie = Movie(TMDB_ID=tmdb_id)
                    db.session.add(movie)

                movie.title = title
                movie.releaseYear = year
                movie.synopsis = synopsis
                movie.thumbnailURL = (
                    "https://image.tmdb.org/t/p/w500/" + thumbnailURL
                )

                movie.directors = [
                    directors[name] for name in movie_directors
                ]

                movie.genres = [
                    genres[name] for name in movie_genres
                ]

                movies[title] = movie

            db.session.flush()

            # 4. USERS
            user_data = [
                ("shaniqu34", "moviefan1@example.com", "shaniqu34@yopmail.com!"),
                ("carmenWillow34", "moviefan2@example.com", "carmenWillow34@yopmail.com!"),
            ]

            users = {}

            for username, email, password in user_data:
                user = User.query.filter_by(
                    userName=username
                ).first()

                if user is None:
                    user = User.query.filter_by(
                        email=email
                    ).first()

                if user is None:
                    user = User(
                        userName=username,
                        email=email,
                        userPassword=generate_password_hash(password),
                    )
                    db.session.add(user)

                users[username] = user

            db.session.flush()

            
            collection_data = [
                ("shaniqu34", "Inception", Decimal("9.0")),
                ("shaniqu34", "Interstellar", Decimal("9.5")),
                ("shaniqu34", "The Dark Knight", Decimal("9.0")),
                ("shaniqu34", "The Matrix", Decimal("8.5")),
                ("shaniqu34", "Avatar", Decimal("8.0")),
                ("carmenWillow34", "Titanic", Decimal("8.5")),
                ("carmenWillow34", "The Lion King", Decimal("9.0")),
                ("carmenWillow34", "Toy Story", Decimal("9.0")),
                ("carmenWillow34", "Get Out", Decimal("8.0")),
            ]

            for username, title, rating in collection_data:
                user = users[username]
                movie = movies[title]

                collection = UserCollection.query.filter_by(
                    userID=user.userID,
                    movieID=movie.movieID,
                ).first()

                if collection is None:
                    db.session.add(
                        UserCollection(
                            user=user,
                            movie=movie,
                            rating=rating,
                        )
                    )
                else:
                    collection.rating = rating

            

            for title, movie in movies.items():
                rating = ThirdPartyRating.query.filter_by(
                    movieID=movie.movieID,
                    externalRater="Demo Source",
                ).first()

                if rating is None:
                    rating = ThirdPartyRating(
                        movieID=movie.movieID,
                        userID=users["shaniqu34"].userID,
                        externalRater="Demo Source",
                        ratingValue="Not verified",
                    )
                    db.session.add(rating)

            # Save all changes.
            db.session.commit()

            print("Seeding completed successfully!")
            print("Genres:", Genre.query.count())
            print("Directors:", Director.query.count())
            print("Movies:", Movie.query.count())
            print("Users:", User.query.count())
            print("Collections:", UserCollection.query.count())
            print("Third-party ratings:", ThirdPartyRating.query.count())

        except Exception:
            db.session.rollback()
            raise


if __name__ == "__main__":
    data_seeding()