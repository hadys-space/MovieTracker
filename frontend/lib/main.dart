
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import 'models/movie.dart';
import 'services/movie_service.dart';
import 'screens/login_screen.dart';
import 'screens/registration_screen.dart';
import 'screens/movie_collection_screen.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'MovieTracker',
      themeMode: ThemeMode.system,
      theme: ThemeData(
        brightness: Brightness.light,
        primarySwatch: Colors.teal,
        scaffoldBackgroundColor: Colors.white,
      ),
      darkTheme: ThemeData(
        brightness: Brightness.dark,
        primarySwatch: Colors.purple,
      ),
      initialRoute: '/',
      routes: {
        '/': (context) => const MyHomePage(),
        '/login': (context) => LoginScreen(
              onLoginSuccess: () {
                Navigator.of(context).pushNamedAndRemoveUntil(
                  '/collection',
                  (route) => false,
                );
              },
            ),
        '/register': (context) => const RegisterScreen(),
        '/collection': (context) => const CollectionScreen(),
      },
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key});

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  final TextEditingController _searchController =
      TextEditingController();

  final MovieService movieService = MovieService();

  final FlutterSecureStorage _storage =
      const FlutterSecureStorage();

  late Future<List<Movie>> moviesFuture;

  List<Movie> _searchResults = [];

  bool _isLoggedIn = false;
  bool _isSearching = false;
  bool _hasSearched = false;
  bool _isAddingMovie = false;

  String _searchSource = 'catalogue';
  String? _searchError;

  @override
  void initState() {
    super.initState();

    moviesFuture = movieService.fetchMovies();

    checkLoginStatus();
  }

  Future<void> checkLoginStatus() async {
    final token = await _storage.read(key: 'access_token');

    if (!mounted) return;

    setState(() {
      _isLoggedIn = token != null && token.isNotEmpty;
    });
  }

  // Search movies by title, genre or director.
  Future<void> searchMovies() async {
    final query = _searchController.text.trim();

    if (query.isEmpty) {
      clearSearch();
      return;
    }

    setState(() {
      _isSearching = true;
      _hasSearched = true;
      _searchError = null;
      _searchResults = [];
    });

    try {
      final result = await movieService.searchMovies(query);

      if (!mounted) return;

      setState(() {
        _searchSource = result['source'];
        _searchResults = result['movies'];
        _isSearching = false;
      });
    } catch (e) {
      if (!mounted) return;

      setState(() {
        _isSearching = false;
        _searchError = e.toString();
      });
    }
  }

  // Clear search and return to the original catalogue.
  void clearSearch() {
    _searchController.clear();

    setState(() {
      _hasSearched = false;
      _searchResults = [];
      _searchError = null;
      _searchSource = 'catalogue';
    });
  }

  // Add a movie to the logged-in user's collection.
  Future<void> addMovieToCollection(String movieID) async {
    final accessToken = await _storage.read(key: 'access_token');

    if (!mounted) return;

    if (accessToken == null || accessToken.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text(
            'Please log in to add movies to your collection.',
          ),
        ),
      );
      return;
    }

    try {
      final response = await http.post(
        Uri.parse(
          'http://127.0.0.1:5000/add-to-movie-collections',
        ),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $accessToken',
        },
        body: jsonEncode({
          'movieID': movieID,
        }),
      );

      if (!mounted) return;

      debugPrint('Movie ID: $movieID');
      debugPrint('Add collection status: ${response.statusCode}');
      debugPrint('Add collection response: ${response.body}');

      final responseData = jsonDecode(response.body);

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            responseData['message'] ?? 'Unable to add movie.',
          ),
        ),
      );
    } catch (e) {
      if (!mounted) return;

      debugPrint('Add collection error: $e');

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Could not connect to the server.'),
        ),
      );
    }
  }

  // Handle both local catalogue movies and TMDB movies.
  Future<void> handleAddMovie(Movie movie) async {
    // If the movie already has a local ID, add it directly.
    if (movie.movieID != null && movie.movieID!.isNotEmpty) {
      await addMovieToCollection(movie.movieID!);
      return;
    }

    // Otherwise, add the selected TMDB movie to our database first.
    if (movie.tmdbId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('This movie does not have a TMDB ID.'),
        ),
      );
      return;
    }

    setState(() {
      _isAddingMovie = true;
    });

    try {
      final newMovieID = await movieService.addMovieToCatalogue(
        movie.tmdbId!,
      );

      if (!mounted) return;

      setState(() {
        moviesFuture = movieService.fetchMovies();
        _isAddingMovie = false;
      });

      await addMovieToCollection(newMovieID);

      // Refresh the search results after adding the movie.
      if (_hasSearched) {
        await searchMovies();
      }
    } catch (e) {
      if (!mounted) return;

      setState(() {
        _isAddingMovie = false;
      });

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Unable to add movie: $e'),
        ),
      );
    }
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Popcorn and M&M Vault',
          style: TextStyle(
            color: Colors.teal,
            fontWeight: FontWeight.bold,
          ),
        ),
        actions: [
          if (_isLoggedIn)
            TextButton(
              onPressed: () {
                Navigator.pushNamed(context, '/collection');
              },
              child: const Text('My Collection'),
            )
          else ...[
            TextButton(
              onPressed: () {
                Navigator.pushNamed(context, '/login').then((_) {
                  checkLoginStatus();
                });
              },
              child: const Text('Login'),
            ),
            TextButton(
              onPressed: () {
                Navigator.pushNamed(context, '/register');
              },
              child: const Text('Register'),
            ),
          ],
          const SizedBox(width: 10),
        ],
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              
              const SizedBox(height: 10),
              const Text(
                'Forgetting your favourite movies? '
                'Just add them to your collection.',
                style: TextStyle(fontSize: 21),
              ),
              const SizedBox(height: 20),

              // Search bar.
              TextField(
                controller: _searchController,
                textInputAction: TextInputAction.search,
                onSubmitted: (_) => searchMovies(),
                decoration: InputDecoration(
                  hintText: 'Search movie by title, genre or director',
                  prefixIcon: const Icon(Icons.search),
                  suffixIcon: IconButton(
                    icon: Icon(
                      _hasSearched ? Icons.close : Icons.search,
                    ),
                    onPressed: _hasSearched
                        ? clearSearch
                        : searchMovies,
                  ),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),

              const SizedBox(height: 25),

              Text(
                _hasSearched ? 'Search Results' : 'Browse Movies',
                style: const TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                ),
              ),

              if (_hasSearched && !_isSearching)
                Padding(
                  padding: const EdgeInsets.only(top: 5),
                  child: Text(
                    _searchSource == 'catalogue'
                        ? 'Results from your movie catalogue'
                        : 'Results from TMDB',
                    style: const TextStyle(
                      fontSize: 13,
                      color: Colors.grey,
                    ),
                  ),
                ),

              const SizedBox(height: 15),

              if (_isSearching)
                const Center(
                  child: Padding(
                    padding: EdgeInsets.all(20),
                    child: CircularProgressIndicator(),
                  ),
                )
              else if (_searchError != null)
                Center(
                  child: Text(
                    _searchError!,
                    textAlign: TextAlign.center,
                  ),
                )
              else if (_hasSearched && _searchResults.isEmpty)
                const Center(
                  child: Text('No movies found.'),
                )
              else if (_hasSearched)
                buildMovieGrid(_searchResults)
              else
                FutureBuilder<List<Movie>>(
                  future: moviesFuture,
                  builder: (context, snapshot) {
                    if (snapshot.connectionState ==
                        ConnectionState.waiting) {
                      return const Center(
                        child: CircularProgressIndicator(),
                      );
                    }

                    if (snapshot.hasError) {
                      return Center(
                        child: Text(
                          'Unable to load movies: ${snapshot.error}',
                        ),
                      );
                    }

                    if (!snapshot.hasData ||
                        snapshot.data!.isEmpty) {
                      return const Center(
                        child: Text('No movies found.'),
                      );
                    }

                    return buildMovieGrid(snapshot.data!);
                  },
                ),
            ],
          ),
        ),
      ),
    );
  }

  Widget buildMovieGrid(List<Movie> movies) {
    return LayoutBuilder(
      builder: (context, constraints) {
        int crossAxisCount;

        if (constraints.maxWidth > 800) {
          crossAxisCount = 5;
        } else if (constraints.maxWidth > 550) {
          crossAxisCount = 3;
        } else {
          crossAxisCount = 2;
        }

        return GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: movies.length,
          gridDelegate:
              SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: crossAxisCount,
            crossAxisSpacing: 12,
            mainAxisSpacing: 12,
            childAspectRatio: 0.65,
          ),
          itemBuilder: (context, index) {
            final movie = movies[index];

            return MovieCard(
              movie: movie,
              isAddingMovie: _isAddingMovie,
              onAddToCollection: () {
                handleAddMovie(movie);
              },
            );
          },
        );
      },
    );
  }
}

class MovieCard extends StatelessWidget {
  final Movie movie;
  final VoidCallback onAddToCollection;
  final bool isAddingMovie;

  const MovieCard({
    super.key,
    required this.movie,
    required this.onAddToCollection,
    this.isAddingMovie = false,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      clipBehavior: Clip.antiAlias,
      elevation: 3,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(
            child: movie.thumbnailURL.isNotEmpty
                ? Image.network(
                    movie.thumbnailURL,
                    width: double.infinity,
                    fit: BoxFit.cover,
                    errorBuilder: (context, error, stackTrace) {
                      return const Center(
                        child: Icon(
                          Icons.movie,
                          size: 50,
                        ),
                      );
                    },
                  )
                : const Center(
                    child: Icon(
                      Icons.movie,
                      size: 50,
                    ),
                  ),
          ),
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  movie.title,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 5),
                Text(
                  movie.directors.isNotEmpty
                      ? 'Director: ${movie.directors.join(', ')}'
                      : 'Director: Unknown',
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
                Text(
                  movie.rating != null
                      ? 'Third Party Rating: ${movie.rating}'
                      : 'Third Party Rating: Not available',
                ),
                const SizedBox(height: 8),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: isAddingMovie
                        ? null
                        : onAddToCollection,
                    child: Text(
                      isAddingMovie
                          ? 'Adding...'
                          : 'Add to Collection',
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
