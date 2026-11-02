
from sqlalchemy import text
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy import UniqueConstraint
from extensions import db

# Movies and Directors relationship
MovieDirectors = db.Table(
    
    "MovieDirectors",
    db.Column(
        "movieID",
        UNIQUEIDENTIFIER(as_uuid=True),
        db.ForeignKey("dbo.Movies.movieID"),
        primary_key=True,
        nullable=False,
    ),
    db.Column(
        "directorID",
        UNIQUEIDENTIFIER(as_uuid=True),
        db.ForeignKey("dbo.Directors.directorID"),
        primary_key=True,
        nullable=False,
       
    ),
     schema= "dbo",
)



MovieGenres = db.Table(
    "MovieGenres",
    db.Column(
        "movieID",
        UNIQUEIDENTIFIER(as_uuid=True),
        db.ForeignKey("dbo.Movies.movieID"),
        primary_key=True,
        nullable=False,
    ),
    db.Column(
        "genreID",
        UNIQUEIDENTIFIER(as_uuid=True),
        db.ForeignKey("dbo.Genres.genreID"),
        primary_key=True,
        nullable=False,
    ),
     schema= "dbo",
)


class User(db.Model):
    __tablename__ = "Users"
    __table_args__ = {"schema": "dbo"}

    userID = db.Column(
        UNIQUEIDENTIFIER(as_uuid=True),
        primary_key=True,
        nullable=False,
        server_default=text("NEWSEQUENTIALID()"),
    )
    userName = db.Column(db.String(25), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    userPassword = db.Column(db.Unicode(255), nullable=False)

    collections = db.relationship(
        "UserCollection",
        back_populates="user",
    )


class Director(db.Model):
    __tablename__ = "Directors"
    __table_args__ = {"schema": "dbo"}

    directorID = db.Column(
        UNIQUEIDENTIFIER(as_uuid=True),
        primary_key=True,
        nullable=False,
        server_default=text("NEWSEQUENTIALID()"),
    )
    directorName = db.Column(db.Unicode(50), unique=True, nullable=False)

    movies = db.relationship(
        "Movie",
        secondary=MovieDirectors,
        back_populates="directors",
    )


class Genre(db.Model):
    __tablename__ = "Genres"
    __table_args__ = {"schema": "dbo"}

    genreID = db.Column(
        UNIQUEIDENTIFIER(as_uuid=True),
        primary_key=True,
        nullable=False,
        server_default=text("NEWSEQUENTIALID()"),
    )
    genre = db.Column(db.String(25), nullable=False)

    movies = db.relationship(
        "Movie",
        secondary=MovieGenres,
        back_populates="genres",
    )


class Movie(db.Model):
    __tablename__ = "Movies"
    __table_args__ = {"schema": "dbo"}

    movieID = db.Column(
        UNIQUEIDENTIFIER(as_uuid=True),
        primary_key=True,
        nullable=False,
        server_default=text("NEWSEQUENTIALID()"),
    )
    TMDB_ID = db.Column(db.Integer, nullable=True)
    thumbnailURL = db.Column(db.Unicode(500), nullable=True)
    title = db.Column(db.Unicode(200), nullable=False)
    releaseYear = db.Column(db.SmallInteger, nullable=True)
    synopsis = db.Column(db.Unicode(None), nullable=True)

    directors = db.relationship(
        "Director",
        secondary=MovieDirectors,
        back_populates="movies",
    )
    genres = db.relationship(
        "Genre",
        secondary=MovieGenres,
        back_populates="movies",
    )
    collections = db.relationship(
        "UserCollection",
        back_populates="movie",
    )
    thirdPartyRatings = db.relationship(
        "ThirdPartyRating",
        back_populates="movie",
    )


class UserCollection(db.Model):
    __tablename__ = "UserCollections"
    __table_args__ = (
        UniqueConstraint(
            "userID",
            "movieID",
            name="Individual_UserCollections"
        ),
        {"schema": "dbo"},
    )

    collectionID = db.Column(
        UNIQUEIDENTIFIER(as_uuid=True),
        primary_key=True,
        nullable=False,
        server_default=text("NEWSEQUENTIALID()"),
    )

    userID = db.Column(
        UNIQUEIDENTIFIER(as_uuid=True),
        db.ForeignKey("dbo.Users.userID"),
        nullable=False,
    )

    movieID = db.Column(
        UNIQUEIDENTIFIER(as_uuid=True),
        db.ForeignKey("dbo.Movies.movieID"),
        nullable=False,
    )

    rating = db.Column(db.Numeric(3, 1), nullable=True)

    user = db.relationship("User", back_populates="collections")
    movie = db.relationship("Movie", back_populates="collections")


class ThirdPartyRating(db.Model):
    __tablename__ = "ThirdPartyRating"
    __table_args__ = {"schema": "dbo"}

    third_Party_Rating = db.Column(
        UNIQUEIDENTIFIER(as_uuid=True),
        primary_key=True,
        nullable=False,
        server_default=text("NEWSEQUENTIALID()"),
    )
    userID = db.Column(UNIQUEIDENTIFIER(as_uuid=True), nullable=True)
    movieID = db.Column(
        UNIQUEIDENTIFIER(as_uuid=True),
        db.ForeignKey("dbo.Movies.movieID"),
        nullable=False,
    )
    externalRater = db.Column(db.String(100), nullable=False)
    ratingValue = db.Column(db.String(30), nullable=False)

    movie = db.relationship("Movie", back_populates="thirdPartyRatings")
