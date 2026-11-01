
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/movie.dart';

class MovieService {
  // Flask API endpoint
  static const String apiUrl =
      'http://127.0.0.1:5000/home-movieDisplay';

  Future<List<Movie>> fetchMovies() async {
    final response = await http.get(Uri.parse(apiUrl));

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);

      final List genres = data['genres'];

      // Store movies using their IDs to avoid duplicates.
      final Map<String, Movie> uniqueMovies = {};

      for (var genre in genres) {
        final List movies = genre['movies'];

        for (var movieData in movies) {
          final movie = Movie.fromJson(movieData);

          uniqueMovies[movie.movieID] = movie;
        }
      }

      return uniqueMovies.values.toList();
    } else {
      throw Exception(
        'Failed to load movies: ${response.statusCode}',
      );
    }
  }
}
