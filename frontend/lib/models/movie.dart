
class Movie {
  final String movieID;
  final String title;
  final String thumbnailURL;
  final double? rating;

  Movie({
    required this.movieID,
    required this.title,
    required this.thumbnailURL,
    this.rating,
  });

  factory Movie.fromJson(Map<String, dynamic> json) {
    final ratings = json['thirdPartyRatings'] as List? ?? [];

    double? movieRating;

    if (ratings.isNotEmpty) {
      final tmdbRating = ratings.firstWhere(
        (item) => item['externalRater'] == 'TMDB',
        orElse: () => null,
      );

      if (tmdbRating != null) {
        movieRating = double.tryParse(
          tmdbRating['ratingValue'].toString(),
        );
      }
    }

    return Movie(
      movieID: json['movieID'] ?? '',
      title: json['title'] ?? 'Unknown Movie',
      thumbnailURL: json['thumbnailURL'] ?? '',
      rating: movieRating,
    );
  }
}
