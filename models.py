from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

# Mock movie data for demonstration
class Movie:
    def __init__(self, id, title, poster_path=None, overview=None, genres=None, video_path=None):
        self.id = id
        self.title = title
        self.poster_path = poster_path or "/static/images/placeholder.png"
        self.overview = overview or "No description available"
        self.genres = genres or "Action, Adventure"
        self.video_path = video_path

# Sample movie data
sample_movies = [
    Movie(1, "The Avengers", "/static/images/placeholder.png", "Earth's mightiest heroes must come together to save the world.", "Action, Adventure"),
    Movie(2, "Inception", "/static/images/placeholder.png", "A thief who steals corporate secrets through dream-sharing technology.", "Sci-Fi, Action"),
    Movie(3, "The Dark Knight", "/static/images/placeholder.png", "Batman fights against the Joker's anarchy in Gotham City.", "Action, Crime"),
    Movie(4, "Pulp Fiction", "/static/images/placeholder.png", "The lives of two mob hitmen, a boxer, and a pair of diner bandits intertwine.", "Crime, Drama"),
    Movie(5, "Forrest Gump", "/static/images/placeholder.png", "The presidencies of Kennedy and Johnson, the events of Vietnam, Watergate, and other historical events unfold through the perspective of an Alabama man.", "Drama, Romance"),
    Movie(6, "The Matrix", "/static/images/placeholder.png", "A computer hacker learns about the true nature of reality and his role in the war against its controllers.", "Sci-Fi, Action"),
]

def get_movie_by_id(movie_id):
    """Get a movie by ID from our sample data"""
    movie_id = int(movie_id)
    for movie in sample_movies:
        if movie.id == movie_id:
            return movie
    return None

def search_movies(query):
    """Search for movies in our sample data"""
    query = query.lower()
    results = []
    for movie in sample_movies:
        if query in movie.title.lower() or query in movie.overview.lower() or query in movie.genres.lower():
            results.append(movie)
    return results
