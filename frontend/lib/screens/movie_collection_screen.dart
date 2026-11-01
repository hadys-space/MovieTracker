
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class CollectionScreen extends StatefulWidget {
  const CollectionScreen({super.key});

  @override
  State<CollectionScreen> createState() => _CollectionScreenState();
}

class _CollectionScreenState extends State<CollectionScreen> {
  final FlutterSecureStorage _storage = FlutterSecureStorage();

  static const String baseUrl = 'http://127.0.0.1:5000';

  List<dynamic> _collections = [];
  bool _isLoading = true;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    fetchCollection();
  }

  Future<void> fetchCollection() async {
    try {
      final token = await _storage.read(key: 'access_token');
      final userID = await _storage.read(key: 'userID');

      if (token == null || userID == null) {
        throw Exception('Login information not found.');
      }

      final response = await http.get(
        Uri.parse('$baseUrl/get-user-collections/$userID'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      final responseData = jsonDecode(response.body);

      if (response.statusCode == 200) {
        if (!mounted) return;

        setState(() {
          _collections = responseData['collections'] ?? [];
          _isLoading = false;
          _errorMessage = null;
        });
      } else {
        throw Exception(
          responseData['message'] ?? 'Unable to load collection.',
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

  void navigateToMovies() {
    Navigator.pushNamed(context, '/movies').then((_) {
      fetchCollection();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('My Movie Collection'),
        centerTitle: true,
        actions: [
          IconButton(
            onPressed: fetchCollection,
            icon: const Icon(Icons.refresh),
            tooltip: 'Refresh collection',
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
                        onPressed: fetchCollection,
                        child: const Text('Try Again'),
                      ),
                    ],
                  ),
                )
              : _collections.isEmpty
                  ? Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const Icon(
                            Icons.movie_outlined,
                            size: 70,
                            color: Colors.grey,
                          ),
                          const SizedBox(height: 15),
                          const Text(
                            'Your collection is empty.\nStart adding movies!',
                            textAlign: TextAlign.center,
                            style: TextStyle(fontSize: 18),
                          ),
                          const SizedBox(height: 20),
                          ElevatedButton.icon(
                            onPressed: navigateToMovies,
                            icon: const Icon(Icons.add),
                            label: const Text(
                              'Add Movie to Collection',
                            ),
                          ),
                        ],
                      ),
                    )
                  : ListView.builder(
                      padding: const EdgeInsets.all(12),
                      itemCount: _collections.length,
                      itemBuilder: (context, index) {
                        final movie = _collections[index];

                        return Card(
                          margin: const EdgeInsets.only(bottom: 15),
                          child: ListTile(
                            contentPadding: const EdgeInsets.all(12),

                            leading: movie['thumbnailURL'] != null
                                ? Image.network(
                                    movie['thumbnailURL'],
                                    width: 70,
                                    fit: BoxFit.cover,
                                    errorBuilder:
                                        (context, error, stackTrace) {
                                      return const Icon(
                                        Icons.movie,
                                        size: 50,
                                      );
                                    },
                                  )
                                : const Icon(
                                    Icons.movie,
                                    size: 50,
                                  ),

                            title: Text(
                              movie['title'] ?? 'Unknown movie',
                              style: const TextStyle(
                                fontWeight: FontWeight.bold,
                              ),
                            ),

                            subtitle: Column(
                              crossAxisAlignment:
                                  CrossAxisAlignment.start,
                              children: [
                                Text(
                                  movie['releaseYear']?.toString() ??
                                      'Release year unavailable',
                                ),
                                Text(
                                  'Genres: ${(movie['genres'] as List).join(', ')}',
                                ),
                                Text(
                                  'My Rating: ${movie['rating'] ?? 'Not rated'}',
                                ),
                              ],
                            ),
                          ),
                        );
                      },
                    ),

      floatingActionButton: !_isLoading && _errorMessage == null
          ? FloatingActionButton.extended(
              onPressed: navigateToMovies,
              icon: const Icon(Icons.add),
              label: const Text('Add Movie'),
            )
          : null,
    );
  }
}
