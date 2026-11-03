# MovieTracker (Popcorn and M&M Vault) – Movie Tracking Application

## 1. Project Overview

MovieTracker is a movie-tracking application designed for movie enthusiasts who want to browse movies and maintain a personal movie collection.

The application allows users to register and log in, browse a movie catalogue, search for movies by title, director or genre, view available third-party movie ratings, and manage their personal collections. Users can also submit personal ratings for movies in their collections.

The application was developed using Flutter for the frontend and Python Flask for the backend, with Microsoft SQL Server used to store application data.

## 2. Technologies and Tools Used

### Backend
- Python 3.13
- Flask
- Flask-SQLAlchemy
- SQLAlchemy
- Flask-Migrate
- PyODBC
- Microsoft ODBC Driver 18 for SQL Server

### Frontend
- Flutter
- Dart

### Database
- Microsoft SQL Server
- SQL Server Management Studio (SSMS)

### Development and Testing
- Git and GitHub
- Postman
- Pytest
- Ruff
- GitHub Actions

## 3. System Requirements

The following software is required to run the application locally:

- Python 3.13
- Flutter SDK and Dart
- Microsoft SQL Server
- SQL Server Management Studio (SSMS)
- Microsoft ODBC Driver 18 for SQL Server
- Git

An internet connection is required for external movie information retrieved through The Movie Database (TMDB) API.

## 4. Installation and Local Setup

### 4.1 Clone the Repository

Open a terminal and run:

```bash
git clone https://github.com/hadys-space/MovieTracker.git
cd MovieTracker
```

### 4.2 Install Backend Dependencies

Upgrade pip and install the required Python packages:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If Pytest is not included in the requirements file, install it separately:

```bash
pip install pytest
```

### 4.3 Configure Environment Variables

The application requires environment-specific configuration, including database credentials and the TMDB API key.

Create a `.env` file in the backend project directory and provide the variables required by the application's configuration.

Example:

```env
SQL_USER_NAME=your_database_username
SQL_PASSWORD=your_database_password
TMDB_API_KEY=your_tmdb_api_key
JWT_SECRET_KEY=your_random_secret_key
```

Use the exact variable names expected by the application's configuration.

Do not commit the `.env` file or expose database credentials, API keys or secret keys in the repository.

## 5. Database Setup

MovieTracker uses Microsoft SQL Server as its relational database management system. The database is named `MovieTrackerDB`.

### 5.1 Create the Database

1. Open SQL Server Management Studio (SSMS).
2. Connect to your SQL Server instance.
3. Open a new query.
4. Execute the following SQL statement:

```sql
CREATE DATABASE MovieTrackerDB;
```

### 5.2 Database Initialization

The application uses SQLAlchemy to communicate with SQL Server.

After configuring the database connection, initialize the database schema using the project's database migration or setup instructions.

If using Flask-Migrate, run the migration commands from the backend project directory:

```bash
flask db upgrade
```

Ensure that the database has the required tables and initial data before using the application.

### 5.3 Creating the Database Tables

If the `MovieTrackerDB` database has been created but the tables are not visible in SQL Server Management Studio, follow these steps to initialize the database schema.

**Step 1: Verify the Database Connection**

1. Open SQL Server Management Studio (SSMS).
2. Connect to the SQL Server instance configured in the application's environment variables.
3. Expand **Databases**.
4. Confirm that `MovieTrackerDB` exists.

**Step 2: Open the Project Directory**

Open a terminal in the backend project directory where `app.py` is located.

Ensure that the Python dependencies have been installed and the database environment variables have been configured.

**Step 3: Apply Database Migrations**

If the project contains Flask-Migrate migration files, run:

```bash
flask db upgrade
```

This applies the existing migrations and creates the database tables.

If Flask cannot locate the application automatically, configure the Flask application entry point before running the command.

For example, in PowerShell:

```powershell
$env:FLASK_APP = "app.py"
flask db upgrade
```

**Step 4: Refresh SQL Server Management Studio**

1. Return to SSMS.
2. Expand `MovieTrackerDB`.
3. Right-click the **Tables** folder.
4. Select **Refresh**.
5. Expand the Tables folder to view the created tables.

**Step 5: Verify the Tables**

Open a new query in SSMS and execute:

```sql
USE MovieTrackerDB;

SELECT TABLE_NAME
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_TYPE = 'Genre';
```

The query should display the tables created by the application's database migrations.

**Troubleshooting**

If the tables still do not appear:

- Confirm that the application is connected to the correct SQL Server instance and database.
- Check that the database username and password are correct.
- Confirm that the `migrations` folder exists in the project.
- Check the terminal for migration errors.
- Ensure that the database user has permission to create and modify tables.

Note: 
- Running `flask db upgrade` requires existing migration files. If no migration files exist, the initial migration must first be generated using Flask-Migrate before the database can be upgraded.

- The database connection settings must match the SQL Server instance configured on the local device.

## 6. Running the Backend

Open a terminal in the backend project directory and run:

```bash
python app.py
```

The Flask application should start and display the local server address in the terminal.

Keep the backend terminal running while using the Flutter application.

## 7. Running the Frontend

Ensure that Flutter is installed and that a supported device or emulator is connected.

Open another terminal and navigate to the frontend directory:

```bash
cd frontend
```
You should see for example: C:\MovieTracker\Frontend

Retrieve the Flutter dependencies:

```bash
flutter pub get
```

Run the application:

```bash
flutter run
```

**Important:** When running the application on a physical mobile device, the frontend must use the computer's local network IP address instead of `127.0.0.1` to communicate with the backend. The computer and mobile device should be connected to the same network.

## 8. Application Features and How to Use MovieTracker

### 8.1 User Registration

New users can create an account by providing the required registration details. Passwords are hashed before being stored in the database.

### 8.2 User Login

Registered users can log in using their account credentials to access the movie catalogue and personal collection.

### 8.3 Browse Movies

Potentionial and current users can browse the available movies displayed in the movie catalogue.

Movie information may include the movie title, release year, synopsis, poster and available third-party ratings.

### 8.4 Search for Movies

Users can search the movie catalogue using a single search field. Searches can be performed using:

- Movie title
- Director's name
- Movie genre

### 8.5 Add Movies to a Personal Collection

Users can select a movie from the catalogue and add it to their personal collection only if they are logged in.

### 8.6 View Personal Collection

Users can access their collection to view the movies they have added.

### 8.7 Rate Movies

Users can submit a personal rating for a movie in their collection. The rating can also be updated.

### 8.8 Remove Movies

Users can remove movies from their personal collection when they are no longer interested in keeping them.

### 8.9 Logout

Users can log out of their account and return to the login screen.

## 9. Third-Party Movie Information

MovieTracker integrates with The Movie Database (TMDB) API to retrieve external movie information.

The application uses the available TMDB information to display movie details and third-party ratings.

A valid TMDB API key must be configured for the relevant external API functionality to work.

External API availability and the information returned are dependent on the third-party service.

## 10. Backend API

The Flask backend exposes endpoints that allow the Flutter frontend to communicate with the database and perform application operations.

The implemented endpoints include:

 `/login` : Authenticates a user. 
 `/register` : Registers a new user. 
 `/home-movieDisplay` : Retrieves movies for the catalogue. 
 `/search` : Searches movies by title, director or genre. 
 `/add-movie` : Adds a movie to the local movie catalogue. 
 `/add-to-movie-collections` : Adds a movie to a user's collection. 
 `/get-user-collections/<user_id>` : Retrieves a user's collection. 
 `/add-rate-movie/<collection_id>` : Adds a personal movie rating. 
 `/update-rate-movie/<collection_id>` : Updates a personal movie rating. 
 `/delete-movie/<collection_id>` : Removes a movie from a collection. 
 `/logout` : Handles the logout request. 

Some endpoints require an authenticated request using the application's JWT authentication mechanism.

## 11. Testing

### Backend Testing

Postman was used to manually test backend API endpoints and verify that requests and responses behaved as expected.

The tests included checking endpoint responses and verifying application operations such as authentication, movie retrieval and collection management.

### Automated Testing

Pytest was included as a testing tool in the development environment. However, a complete automated test suite covering the application's core business rules and API functionality was not completed.

### Frontend Testing

The Flutter mobile application was not fully tested on a physical mobile device. Therefore, mobile compatibility and behaviour have not been completely verified.

## 12. AI-Assisted Feature

### Proposed Feature: Personalized Movie Recommendations

A proposed AI-assisted feature for MovieTracker is a personalized movie recommendation system.

The intended feature would recommend movies to users based on information from their personal collections, including their submitted movie ratings and preferred genres.

The proposed approach was to use a Gemini model to analyse the available collection and rating information and generate relevant movie recommendations.

The recommendation feature was not implemented in the submitted version of the application.

The proposed model and implementation approach would need to be verified before development. No training dataset or model-training process was finalized.

## 13. Continuous Integration

GitHub Actions was included among the development tools considered for the project.

The intended CI process is to install the required dependencies and execute automated tests when changes are pushed to the repository or pull requests are created.

**Implementation status:** Confirm that the GitHub Actions workflow is configured and successfully running before describing CI as completed. If no workflow was completed, this remains an outstanding item.

## 14. Assumptions and Limitations

### Assumptions
- Users have access to a supported device or emulator with Flutter installed.
- Microsoft SQL Server is available and configured before the backend is started.
- Users have a valid database connection configuration.
- A valid TMDB API key is available for external movie information.
- An internet connection is available when retrieving information from external services.

### Incomplete Areas
The following areas were not completed or fully verified in the submitted version:

1. AI-assisted recommendations: The proposed personalized movie recommendation feature was not implemented.
2. Mobile testing: The Flutter application was not fully tested on a physical mobile device.
3. Automated test cases: A complete automated test suite was not developed.
4. Test coverage report: A formal automated test coverage report was not generated.
5. Deployment: A live deployment was not completed. The application is intended to be run locally using the documented setup instructions.

## 15. AI Assistance Disclosure

AI-assisted development tools were used during the development of MovieTracker to support implementation, troubleshooting and documentation.

ChatGPT was used to assist with understanding errors, reviewing code, suggesting corrections and explaining development concepts.

All AI-assisted suggestions were reviewed and adapted during development. The developer remains responsible for understanding and verifying the submitted implementation.

The model was also use to in creating this report; corrections were made by the developer.

AI assistance was used as a development aid and not as a replacement for reviewing and understanding the application's implementation.

**Note**: All images and Third-Part-Ratings are to be attributed to TMDB
