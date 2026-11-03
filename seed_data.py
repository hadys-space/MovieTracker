
from decimal import Decimal
import os
import requests
import time
from werkzeug.security import generate_password_hash
from app import create_movie_app
from extensions import db
from models import (Director, Genre,Movie,ThirdPartyRating,User,UserCollection,)


def seed_tmdb_movies(existing_seeded_movies, target_new_movies=1000):

    api_key = os.getenv("TMDB_API_KEY")

    if not api_key:
        raise ValueError("TMDB_API_KEY was not found.")

    session = requests.Session()

    base_url = "https://api.themoviedb.org/3"

    
    response = session.get(
        f"{base_url}/genre/movie/list",
        params={"api_key": api_key},
        timeout=20
    )

    response.raise_for_status()

    tmdb_genres = {
        item["id"]: item["name"]
        for item in response.json()["genres"]
    }

   
    genre_cache = {
        genre.genre: genre
        for genre in Genre.query.all()
    }

    
    for name in tmdb_genres.values():

        if name not in genre_cache:

            genre = Genre(genre=name)

            db.session.add(genre)

            genre_cache[name] = genre

    db.session.flush()

    
    director_cache = {
        director.directorName: director
        for director in Director.query.all()
    }

    
    existing_tmdb_ids = {
        row[0]
        for row in db.session.query(Movie.TMDB_ID)
        .filter(Movie.TMDB_ID.isnot(None))
        .all()
    }

    # Save or update a TMDB rating
    def save_tmdb_rating(movie, value):

        rating = ThirdPartyRating.query.filter_by(
            movieID=movie.movieID,
            externalRater="TMDB"
        ).first()

        rating_value = (
            f"{float(value):.1f}"
            if value is not None
            else "Not available"
        )

        if rating is None:

            rating = ThirdPartyRating(
                movie=movie,
                userID=None,
                externalRater="TMDB",
                ratingValue=rating_value
            )

            db.session.add(rating)

        else:
            rating.ratingValue = rating_value

   
    for movie in existing_seeded_movies:

        if movie.TMDB_ID is None:
            continue

        response = session.get(
            f"{base_url}/movie/{movie.TMDB_ID}",
            params={"api_key": api_key},
            timeout=20
        )

        response.raise_for_status()

        save_tmdb_rating(
            movie,
            response.json().get("vote_average")
        )


    added_movies = 0
    page = 1
    max_pages = 500

    while added_movies < target_new_movies and page <= max_pages:

        response = session.get(
            f"{base_url}/discover/movie",
            params={
                "api_key": api_key,
                "sort_by": "popularity.desc",
                "include_adult": "false",
                "include_video": "false",
                "page": page
            },
            timeout=20
        )

        response.raise_for_status()

        data = response.json()

        for item in data.get("results", []):

            if added_movies >= target_new_movies:
                break

            tmdb_id = item["id"]

           
            if tmdb_id in existing_tmdb_ids:
                continue

    
            release_date = item.get("release_date")

            release_year = (
                int(release_date[:4])
                if release_date and len(release_date) >= 4
                else None
            )

           
            poster_path = item.get("poster_path")

            thumbnail_url = (
                "https://image.tmdb.org/t/p/w500" + poster_path
                if poster_path
                else None
            )

            
            movie = Movie(
                TMDB_ID=tmdb_id,
                title=item["title"],
                releaseYear=release_year,
                synopsis=item.get("overview"),
                thumbnailURL=thumbnail_url
            )

            db.session.add(movie)

            movie.genres = [
                genre_cache[tmdb_genres[genre_id]]
                for genre_id in item.get("genre_ids", [])
                if genre_id in tmdb_genres
            ]

            try:

                credits_response = session.get(
                    f"{base_url}/movie/{tmdb_id}/credits",
                    params={"api_key": api_key},
                    timeout=20
                )

                credits_response.raise_for_status()

                credits = credits_response.json()

                director_names = [
                    person["name"]
                    for person in credits.get("crew", [])
                    if person.get("job") == "Director"
                ]

                movie.directors = []

                for name in director_names:

                    if name not in director_cache:

                        director = Director(
                            directorName=name
                        )

                        db.session.add(director)

                        director_cache[name] = director

                    movie.directors.append(
                        director_cache[name]
                    )

            except requests.RequestException as error:

                print(
                    f"Could not retrieve directors for "
                    f"{item['title']}: {error}"
                )

            save_tmdb_rating(
                movie,
                item.get("vote_average")
            )

            existing_tmdb_ids.add(tmdb_id)

            added_movies += 1

            if added_movies % 50 == 0:

                print(
                    f"{added_movies} new movies added..."
                )

            time.sleep(0.05)

        if page >= data.get("total_pages", 0):
            break

        page += 1

    ThirdPartyRating.query.filter_by(
        externalRater="Demo Source"
    ).delete(synchronize_session=False)

    print(f"Additional movies added: {added_movies}")

    if added_movies < target_new_movies:

        print(
            "TMDB returned fewer new movies than requested."
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

            seed_tmdb_movies(
                    existing_seeded_movies=movies.values(),
                    target_new_movies=1000
            )
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