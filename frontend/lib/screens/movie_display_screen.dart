
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class MovieCatalogueScreen extends StatefulWidget {
  const MovieCatalogueScreen({super.key});

  @override
  State<MovieCatalogueScreen> createState() =>
      _MovieCatalogueScreenState();
}

class _MovieCatalogueScreenState extends State<MovieCatalogueScreen> {
  final FlutterSecureStorage _storage = FlutterSecureStorage();

  static const String baseUrl = 'http://127.0.0.1:5000';

  List<dynamic> _genres = [];
  bool _isLoading = true;
  String? _errorMessage;

  final Set<String> _addingMovieIds = {};

  @override
  void initState() {
    super.initState();
    fetchMovies();
  }

  Future<void> fetchMovies() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/home-movieDisplay'),
      );

      final responseData = jsonDecode(response.body);

      if (response.statusCode == 200) {
        if (!mounted) return;

        setState(() {
          _genres = responseData['genres'] ?? [];
          _isLoading = false;
          _errorMessage = null;
        });
      } else {
        throw Exception(
          responseData['message'] ?? 'Unable to load movies.',
        );
      }
    } catch (error) {
      if (!mounted) return;

      setState(() {
        _errorMessage = error.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> addMovieToCollection(String movieID) async {
    if (_addingMovieIds.contains(movieID)) return;

    setState(() {
      _addingMovieIds.add(movieID);
    });

    try {
      final token = await _storage.read(key: 'access_token');

      if (token == null) {
        throw Exception(
          'Login information not found. Please log in again.',
        );
      }

      final response = await http.post(
        Uri.parse('$baseUrl/add-to-movie-collections'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'movieID': movieID,
        }),
      );

      final responseData = jsonDecode(response.body);

      if (!mounted) return;

      if (response.statusCode == 201) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              responseData['message'] ??
                  'Movie added successfully.',
            ),
            backgroundColor: Colors.green,
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              responseData['message'] ??
                  'Unable to add movie.',
            ),
            backgroundColor: Colors.red,
          ),
        );
      }
    } catch (error) {
      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error: $error'),
          backgroundColor: Colors.red,
        ),
      );
    } finally {
      if (mounted) {
        setState(() {
          _addingMovieIds.remove(movieID);
        });
      }
    }
  }

  Widget buildMovieCard(dynamic movie) {
    final String movieID = movie['movieID'].toString();
    final bool isAdding = _addingMovieIds.contains(movieID);

    final ratings = movie['thirdPartyRatings'] as List? ?? [];

    return Card(
      margin: const EdgeInsets.symmetric(
        horizontal: 12,
        vertical: 6,
      ),
      child: Padding(
        padding: const EdgeInsets.all(10),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            movie['thumbnailURL'] != null &&
                    movie['thumbnailURL'].toString().isNotEmpty
                ? Image.network(
                    movie['thumbnailURL'],
                    width: 85,
                    height: 125,
                    fit: BoxFit.cover,
                    errorBuilder: (context, error, stackTrace) {
                      return const SizedBox(
                        width: 85,
                        height: 125,
                        child: Icon(
                          Icons.movie,
                          size: 50,
                        ),
                      );
                    },
                  )
                : const SizedBox(
                    width: 85,
                    height: 125,
                    child: Icon(
                      Icons.movie,
                      size: 50,
                    ),
                  ),

            const SizedBox(width: 12),

            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    movie['title'] ?? 'Unknown movie',
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),

                  const SizedBox(height: 8),

                  if (ratings.isNotEmpty)
                    ...ratings.map((rating) {
                      return Text(
                        '${rating['externalRater']}: '
                        '${rating['ratingValue']}',
                        style: const TextStyle(fontSize: 12),
                      );
                    }),

                  const SizedBox(height: 12),

                  ElevatedButton.icon(
                    onPressed: isAdding
                        ? null
                        : () => addMovieToCollection(movieID),
                    icon: isAdding
                        ? const SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                            ),
                          )
                        : const Icon(Icons.add),
                    label: Text(
                      isAdding ? 'Adding...' : 'Add to Collection',
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Browse Movies'),
        centerTitle: true,
        actions: [
          IconButton(
            onPressed: fetchMovies,
            icon: const Icon(Icons.refresh),
            tooltip: 'Refresh movies',
          ),
        ],
      ),

      body: _isLoading
          ? const Center(
              child: CircularProgressIndicator(),
            )
          : _errorMessage != null
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        _errorMessage!,
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 15),
                      ElevatedButton(
                        onPressed: fetchMovies,
                        child: const Text('Try Again'),
                      ),
                    ],
                  ),
                )
              : _genres.isEmpty
                  ? const Center(
                      child: Text('No movies available.'),
                    )
                  : ListView.builder(
                      padding: const EdgeInsets.only(bottom: 20),
                      itemCount: _genres.length,
                      itemBuilder: (context, index) {
                        final genre = _genres[index];
                        final movies =
                            genre['movies'] as List? ?? [];

                        return ExpansionTile(
                          initiallyExpanded: true,
                          title: Text(
                            genre['genre'] ?? 'Unknown genre',
                            style: const TextStyle(
                              fontWeight: FontWeight.bold,
                              fontSize: 18,
                            ),
                          ),
                          subtitle: Text(
                            '${movies.length} movies',
                          ),
                          children: movies.isEmpty
                              ? [
                                  const Padding(
                                    padding: EdgeInsets.all(12),
                                    child: Text(
                                      'No movies in this genre.',
                                    ),
                                  ),
                                ]
                              : movies.map((movie) {
                                  return buildMovieCard(movie);
                                }).toList(),
                        );
                      },
                    ),
    );
  }
}
