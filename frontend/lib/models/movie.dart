
class Movie {
  final String? movieID;
  final int? tmdbId;
  final String title;
  final String thumbnailURL;
  final double? rating;
  final int? releaseYear;
  final String? synopsis;
  final List<String> directors;

  Movie({
    this.movieID,
    this.tmdbId,
    required this.title,
    required this.thumbnailURL,
    this.rating,
    this.releaseYear,
    this.synopsis,
    this.directors = const[],
  });

  factory Movie.fromJson(Map<String, dynamic> json) {
    final ratings = json['thirdPartyRatings'] as List? ?? [];

    double? movieRating;

    for (final item in ratings) {
      if (item is Map &&
          item['externalRater'] == 'TMDB') {
        movieRating = double.tryParse(
          item['ratingValue'].toString(),
        );
        break;
      }
    }

    // Also support a direct ratingValue from TMDB search results.
    movieRating ??= double.tryParse(
      (json['ratingValue'] ?? json['vote_average'] ?? '').toString(),
    );

    return Movie(
      movieID: json['movieID']?.toString(),
      tmdbId: int.tryParse(
        (json['TMDB_ID'] ?? json['tmdbId'] ?? '').toString(),
      ),
      title: json['title'] ?? 'Unknown Movie',
      thumbnailURL: json['thumbnailURL'] ?? '',
      rating: movieRating,
      releaseYear: int.tryParse(
        (json['releaseYear'] ?? '').toString(),
      ),
      synopsis: json['synopsis']?.toString(),
      directors: List <String>.from(json['directors'] ?? []),
    );
  }
}
