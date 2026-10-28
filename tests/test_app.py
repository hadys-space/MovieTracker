from app import create_movie_app


def test_homepage():
    app = create_movie_app(testing=True)
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert response.get_json() == {
        "message": "This is the Movie Tracker API!"
    }
