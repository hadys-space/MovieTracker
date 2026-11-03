
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
  final FlutterSecureStorage _storage =
      const FlutterSecureStorage();

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

      if (token == null || token.isEmpty || userID == null || userID.isEmpty) {
        throw Exception('Login information not found.');
      }

      final response = await http.get(
        Uri.parse('$baseUrl/get-user-collections/$userID'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      if (!mounted) return;

      final responseData = jsonDecode(response.body);

      if (response.statusCode == 200) {
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

  String getGenres(dynamic genres) {
    if (genres == null || genres is! List || genres.isEmpty) {
      return 'No genres available';
    }

    return genres.map((genre) {
      if (genre is Map) {
        return genre['genre']?.toString() ?? '';
      }

      return genre.toString();
    }).where((genre) => genre.isNotEmpty).join(', ');
  }

  String getThirdPartyRatings(dynamic ratings) {
    if (ratings == null || ratings is! List || ratings.isEmpty) {
      return 'No third-party ratings available.';
    }

    return ratings.map((rating) {
      if (rating is! Map) {
        return rating.toString();
      }

      final source = rating['externalRater'] ?? 'Unknown source';
      final value = rating['ratingValue'] ?? 'N/A';

      return '$source: $value';
    }).join('\n');
  }

  Future<void> rateMovie(
    String collectionID,
    dynamic currentRating,
  ) async {
    final isUpdating = currentRating != null;

    final newRating = await showDialog<double>(
      context: context,
      builder: (dialogContext) {
        return RatingDialog(
          currentRating: currentRating,
          isUpdating: isUpdating,
        );
      },
    );

    if (newRating == null || !mounted) return;

    final token = await _storage.read(key: 'access_token');

    if (!mounted) return;

    if (token == null || token.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please log in again.'),
        ),
      );
      return;
    }

    try {
      final endpoint = isUpdating
          ? 'update-rate-movie'
          : 'add-rate-movie';

      final uri = Uri.parse(
        '$baseUrl/$endpoint/$collectionID',
      );

      // Use PUT when updating and POST when adding a rating.
      final response = isUpdating
          ? await http.put(
              uri,
              headers: {
                'Authorization': 'Bearer $token',
                'Content-Type': 'application/json',
              },
              body: jsonEncode({
                'rating': newRating,
              }),
            )
          : await http.post(
              uri,
              headers: {
                'Authorization': 'Bearer $token',
                'Content-Type': 'application/json',
              },
              body: jsonEncode({
                'rating': newRating,
              }),
            );

      if (!mounted) return;

      final responseData = jsonDecode(response.body);

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            responseData['message'] ?? 'Unable to save rating.',
          ),
        ),
      );

      if (response.statusCode == 200 ||
          response.statusCode == 201) {
        await fetchCollection();
      }
    } catch (error) {
      if (!mounted) return;

      debugPrint('Rating error: $error');

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Could not connect to the server.'),
        ),
      );
    }
  }

  Future<void> deleteMovieFromCollection(
    String collectionID,
  ) async {
    final token = await _storage.read(key: 'access_token');

    if (!mounted) return;

    if (token == null || token.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please log in again.'),
        ),
      );
      return;
    }

    final confirmDelete = await showDialog<bool>(
      context: context,
      builder: (dialogContext) {
        return AlertDialog(
          title: const Text('Remove Movie'),
          content: const Text(
            'Are you sure you want to remove this movie '
            'from your collection?',
          ),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.pop(dialogContext, false);
              },
              child: const Text('Cancel'),
            ),
            TextButton(
              onPressed: () {
                Navigator.pop(dialogContext, true);
              },
              child: const Text('Delete'),
            ),
          ],
        );
      },
    );

    if (confirmDelete != true || !mounted) return;

    try {
      final response = await http.delete(
        Uri.parse('$baseUrl/delete-movie/$collectionID'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      if (!mounted) return;

      final responseData = jsonDecode(response.body);

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            responseData['message'] ?? 'Unable to remove movie.',
          ),
        ),
      );

      if (response.statusCode == 200) {
        await fetchCollection();
      }
    } catch (error) {
      if (!mounted) return;

      debugPrint('Delete movie error: $error');

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Could not connect to the server.'),
        ),
      );
    }
  }

  
  Future<void> navigateToMovies() async {
    await Navigator.pushNamed(context, '/');

    if (!mounted) return;

    await fetchCollection();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('My Movie Collection'),
        centerTitle: true,
        actions: [
          TextButton.icon(
            onPressed: navigateToMovies,
            icon: const Icon(Icons.movie),
            label: const Text('Browse Movies'),
          ),
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

                        final collectionID =
                            movie['collectionID']?.toString();

                        final currentRating = movie['rating'];

                        return Card(
                          margin: const EdgeInsets.only(bottom: 15),
                          child: ListTile(
                            contentPadding:
                                const EdgeInsets.all(12),

                            leading: movie['thumbnailURL'] != null &&
                                    movie['thumbnailURL']
                                        .toString()
                                        .isNotEmpty
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
                                  movie['directors'] != null &&
                                          (movie['directors'] as List).isNotEmpty
                                      ? 'Director: ${(movie['directors'] as List).join(', ')}'
                                      : 'Director: Unknown',
                                  maxLines: 2,
                                  overflow: TextOverflow.ellipsis,
                                ),

                                Text(
                                  'Genres: ${getGenres(movie['genres'])}',
                                ),

                                const SizedBox(height: 8),

                                // User's personal rating.
                                Row(
                                  children: [
                                    const Icon(
                                      Icons.star,
                                      color: Colors.amber,
                                      size: 20,
                                    ),
                                    const SizedBox(width: 5),
                                    Text(
                                      currentRating != null
                                          ? 'My Rating: $currentRating / 10'
                                          : 'My Rating: Not rated',
                                    ),
                                  ],
                                ),

                                const SizedBox(height: 10),

                                // Third-party ratings.
                                const Text(
                                  'Third-Party Ratings:',
                                  style: TextStyle(
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),

                                const SizedBox(height: 4),

                                Text(
                                  getThirdPartyRatings(
                                    movie['thirdPartyRatings'],
                                  ),
                                ),

                                const SizedBox(height: 5),

                                TextButton.icon(
                                  onPressed: collectionID == null
                                      ? null
                                      : () {
                                          rateMovie(
                                            collectionID,
                                            currentRating,
                                          );
                                        },
                                  icon: Icon(
                                    currentRating == null
                                        ? Icons.star_outline
                                        : Icons.edit,
                                  ),
                                  label: Text(
                                    currentRating == null
                                        ? 'Rate Movie'
                                        : 'Update Rating',
                                  ),
                                ),
                              ],
                            ),

                            // Delete button.
                            trailing: IconButton(
                              onPressed: collectionID == null
                                  ? null
                                  : () {
                                      deleteMovieFromCollection(
                                        collectionID,
                                      );
                                    },
                              icon: const Icon(
                                Icons.delete,
                                color: Colors.red,
                              ),
                              tooltip: 'Remove from collection',
                            ),
                          ),
                        );
                      },
                    ),

      floatingActionButton:
          !_isLoading && _errorMessage == null
              ? FloatingActionButton.extended(
                  onPressed: navigateToMovies,
                  icon: const Icon(Icons.add),
                  label: const Text('Add Movie'),
                )
              : null,
    );
  }
}

class RatingDialog extends StatefulWidget {
  final dynamic currentRating;
  final bool isUpdating;

  const RatingDialog({
    super.key,
    required this.currentRating,
    required this.isUpdating,
  });

  @override
  State<RatingDialog> createState() => _RatingDialogState();
}

class _RatingDialogState extends State<RatingDialog> {
  late final TextEditingController ratingController;

  final GlobalKey<FormState> ratingFormKey =
      GlobalKey<FormState>();

  @override
  void initState() {
    super.initState();

    ratingController = TextEditingController(
      text: widget.currentRating?.toString() ?? '',
    );
  }

  @override
  void dispose() {
    ratingController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text(
        widget.isUpdating
            ? 'Update Movie Rating'
            : 'Rate Movie',
      ),
      content: Form(
        key: ratingFormKey,
        child: TextFormField(
          controller: ratingController,
          autofocus: true,
          keyboardType: const TextInputType.numberWithOptions(
            decimal: true,
          ),
          decoration: const InputDecoration(
            labelText: 'Your Rating',
            hintText: 'Enter a rating from 0 to 10',
            suffixText: '/ 10',
            border: OutlineInputBorder(),
          ),
          validator: (value) {
            if (value == null || value.trim().isEmpty) {
              return 'Please enter a rating.';
            }

            final rating = double.tryParse(value.trim());

            if (rating == null ||
                !rating.isFinite ||
                rating < 0 ||
                rating > 10) {
              return 'Enter a valid rating from 0 to 10.';
            }

            return null;
          },
        ),
      ),
      actions: [
        TextButton(
          onPressed: () {
            Navigator.pop(context);
          },
          child: const Text('Cancel'),
        ),
        ElevatedButton(
          onPressed: () {
            if (ratingFormKey.currentState!.validate()) {
              final rating = double.parse(
                ratingController.text.trim(),
              );

              Navigator.pop(context, rating);
            }
          },
          child: const Text('Save Rating'),
        ),
      ],
    );
  }
}
