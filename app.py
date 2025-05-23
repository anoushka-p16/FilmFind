# Imports and setup
from flask import Flask, request, jsonify, abort, render_template, url_for, redirect
from sqlalchemy import or_
from models import db, MovieModel

# Create Flask app, configure SQLite DB, connect SQLALchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# The HTML Views ____________________________________________________________
# Main and Landing page - main.html
@app.route('/')
def home_redirect():
    return render_template('main.html')

# Fetching all movies from DB and passing to the index.html template
@app.route('/movies')
def view_all_movies():
    q = MovieModel.query

    search = request.args.get('search')
    genre = request.args.get('genre')
    director = request.args.get('director')
    year = request.args.get('year')

    if search:
        q = q.filter(MovieModel.title.ilike(f"%{search}%"))
    if genre:
        q = q.filter(MovieModel.genre.ilike(f"%{genre}%"))
    if director:
        q = q.filter(MovieModel.director == director)
    if year:
        q = q.filter(MovieModel.year == int(year))

    movies = q.order_by(MovieModel.id.asc()).all()

    # Build genre dropdown with individual items
    raw_genres = db.session.query(MovieModel.genre).filter(MovieModel.genre != None).all()
    genre_set = set()
    for row in raw_genres:
        split_genres = [g.strip() for g in row[0].split(',')]
        genre_set.update(split_genres)
    genres = sorted(genre_set)

    # Same for director and year
    directors = [row[0] for row in db.session.query(MovieModel.director).distinct().order_by(MovieModel.director).all()]
    years = [row[0] for row in db.session.query(MovieModel.year).distinct().order_by(MovieModel.year).all()]

    return render_template("index.html", movies=movies, genres=genres, directors=directors, years=years)

@app.route('/filter-movies')
def filter_movies():
    q = MovieModel.query

    search = request.args.get('search')
    genre = request.args.get('genre')
    director = request.args.get('director')
    year = request.args.get('year')

    if search:
        q = q.filter(MovieModel.title.ilike(f"%{search}%"))
    if genre:
        q = q.filter(MovieModel.genre.ilike(f"%{genre}%"))
    if director:
        q = q.filter(MovieModel.director == director)
    if year:
        q = q.filter(MovieModel.year == int(year))

    movies = q.order_by(MovieModel.id.asc()).all()
    return render_template('_movie_cards.html', movies=movies)

@app.route('/movies/<int:movie_id>/remove_from_list', methods=['POST'])
def remove_from_my_list(movie_id):
    movie = MovieModel.query.get_or_404(movie_id)
    movie.in_my_list = False
    db.session.commit()
    return redirect(url_for('my_list'))

# Only display movies that are in user's list
@app.route('/my-list')
def my_list():
    movies = MovieModel.query.filter_by(in_my_list=True).order_by(MovieModel.id.asc()).all()
    return render_template('myList.html', movies=movies)

# Loads page for single movie, sends 404 error if not found
@app.route('/movies/<int:movie_id>')
def movie_detail(movie_id):
    movie = MovieModel.query.get_or_404(movie_id)
    return render_template('detail.html', movie=movie)

# Login page
@app.route('/login')
def login():
    return render_template('login.html')

# The API ___________________________________________________________________

# POST to my list
@app.route('/movies/<int:movie_id>/add_to_list', methods=['POST'])
def add_to_my_list(movie_id):
    movie = MovieModel.query.get_or_404(movie_id)
    movie.in_my_list = True
    db.session.commit()
    return redirect(url_for('movie_detail', movie_id=movie_id))

# GET all movies
@app.route('/api/movies', methods=['GET'])
def api_list_movies():
    q = MovieModel.query
    for fld in ('genre','director','year'):
        if v := request.args.get(fld):
            q = q.filter_by(**{fld: v})
    return jsonify([m.json() for m in q.all()])

# GET one movie
@app.route('/api/movies/<int:movie_id>', methods=['GET'])
def get_movie(movie_id):
    m = MovieModel.query.get(movie_id)
    if not m:
        abort(404, "Movie not found")
    return jsonify(m.json())

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='localhost', port=5000, debug=True)
