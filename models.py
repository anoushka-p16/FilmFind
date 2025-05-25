from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# MovieModel class to represent a movie in the DB
# Includes its poster link, title, year, rating, runtime, genre, summary, director, and actors
class MovieModel(db.Model):
    __tablename__ = 'movies'

    id = db.Column(db.Integer, primary_key=True)
    poster = db.Column(db.String(255))
    title = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer)
    rating = db.Column(db.String(10))
    runtime = db.Column(db.Integer)
    genre = db.Column(db.String(80))
    summary = db.Column(db.Text)
    director = db.Column(db.String(80))
    actors = db.Column(db.JSON)

    in_my_list = db.Column(db.Boolean, default=False)

    def __init__(self, poster, title, year, rating, runtime, genre, summary, director, actors):
        self.poster = poster
        self.title = title
        self.year = year
        self.rating = rating
        self.runtime = runtime
        self.genre = genre
        self.summary = summary
        self.director = director
        self.actors = actors

    # JSON representation of the MovieModel
    def json(self):
        return {
            'id': self.id,
            'poster':self.poster,
            'title': self.title,
            'year': self.year,
            'rating': self.rating,
            'runtime': self.runtime,
            'genre': self.genre,
            'summary': self.summary,
            'director': self.director,
            'actors': self.actors,
            'in_my_list': self.in_my_list
        }
    
class ReviewModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)

    movie = db.relationship('MovieModel', backref='reviews')
    user = db.relationship('User', backref='reviews')
