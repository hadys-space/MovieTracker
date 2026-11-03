
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/movie.dart';

class MovieService {
  static const String baseUrl = 'http://127.0.0.1:5000';

  static const String apiUrl =
      '$baseUrl/home-movieDisplay';

  Future<List<Movie>> fetchMovies() async {
    final response = await http.get(Uri.parse(apiUrl));

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);

      final List genres = data['genres'] ?? [];

      final Map<String, Movie> uniqueMovies = {};

      for (var genre in genres) {
        final List movies = genre['movies'] ?? [];

        for (var movieData in movies) {
          final movie = Movie.fromJson(movieData);

          if (movie.movieID != null) {
            uniqueMovies[movie.movieID!] = movie;
          }
        }
      }

      return uniqueMovies.values.toList();
    }

    throw Exception(
      'Failed to load movies: ${response.statusCode}',
    );
  }

Future<Map<String, dynamic>> searchMovies(String query) async {
  final response = await http.get(
    Uri.parse('$baseUrl/search').replace(
      queryParameters: {
        'query': query,
      },
    ),
  );

  final data = jsonDecode(response.body);

  if (response.statusCode == 200) {
    final List results = data['movies'] ?? [];

    final movies = results
        .map((item) => Movie.fromJson(item))
        .toList();

    return {
      'source': data['source'] ?? 'catalogue',
      'movies': movies,
    };
  }

  throw Exception(
    data['message'] ?? 'Unable to search for movies.',
  );
  }
  Future<String> addMovieToCatalogue(int tmdbId) async {
    final response = await http.post(
      Uri.parse('$baseUrl/add-movie'),
      headers: {
        'Content-Type': 'application/json',
      },
      body: jsonEncode({
        'TMDB_ID': tmdbId,
      }),
    );

    final data = jsonDecode(response.body);

    if (response.statusCode != 200 &&
        response.statusCode != 201) {
      throw Exception(
        data['message'] ?? 'Unable to add movie to catalogue.',
      );
    }

    final movieData = data['movie'] is Map
        ? data['movie']
        : data;

    final movieID = movieData['movieID']?.toString();

    if (movieID == null || movieID.isEmpty) {
      throw Exception(
        'Movie was added, but the server did not return its movieID.',
      );
    }

    return movieID;
  }
}