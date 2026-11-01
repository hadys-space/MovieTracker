
import 'package:flutter/material.dart';
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

      // The public movie catalogue is the starting page.
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
  final TextEditingController _searchController = TextEditingController();

  final MovieService movieService = MovieService();

  late Future<List<Movie>> moviesFuture;

  @override
  void initState() {
    super.initState();
    moviesFuture = movieService.fetchMovies();
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
          TextButton(
            onPressed: () {
              Navigator.pushNamed(context, '/login');
            },
            child: const Text('Login'),
          ),

          TextButton(
            onPressed: () {
              Navigator.pushNamed(context, '/register');
            },
            child: const Text('Register'),
          ),

          const SizedBox(width: 10),
        ],
      ),

      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'GRAB YOUR POPCORN & M&MS AND',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),

              const SizedBox(height: 8),

              const Text(
                'DISCOVER YOUR NEXT FAVOURITE MOVIE',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
              ),

              const SizedBox(height: 10),

              const Text(
                'Forgeting your favourite movies? '
                'Just add them to your collection.',
                style: TextStyle(fontSize: 16),
              ),

              const SizedBox(height: 20),

              // Movie search field.
              TextField(
                controller: _searchController,
                decoration: InputDecoration(
                  hintText: 'Search movie by title, genre or director',
                  prefixIcon: const Icon(Icons.search),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),

              const SizedBox(height: 25),

              const Text(
                'Browse Movies',
                style: TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                ),
              ),

              const SizedBox(height: 15),

              // Retrieve and display movies from Flask.
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

                  if (!snapshot.hasData || snapshot.data!.isEmpty) {
                    return const Center(
                      child: Text('No movies found.'),
                    );
                  }

                  final movies = snapshot.data!;

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
                        physics:
                            const NeverScrollableScrollPhysics(),
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

                          return MovieCard(movie: movie);
                        },
                      );
                    },
                  );
                },
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class MovieCard extends StatelessWidget {
  final Movie movie;

  const MovieCard({
    super.key,
    required this.movie,
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
                Text('Third Party Rating: ${movie.rating}'),
              ],
            ),
          ),
        ],
      ),
    );
  }
}