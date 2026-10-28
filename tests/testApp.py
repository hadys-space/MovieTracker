from unittest.mock import patch

from app import create_movie_app


def test_homepage():
   app = create_movie_app(testing=True)
   client = app.test_client()
   response = client.get('/')

   assert response.status_code == 200
   assert response.get_json() == {'message': 'This is the Movie Tracker API!'}

def test_databaseConnection_route():
   app = create_movie_app(testing=True)
   client = app.test_client()

   with patch('app.db.session.query') as mock_query:
         mock_query.return_value.all.return_value = []
         response = client.get('/test-db')
    
         assert response.status_code == 200
         assert response.get_json() == {
              'message': 'Database query successful!',
              'genre_count': 0,
              'genres': []
         }