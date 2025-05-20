# Imports and setup
from flask import Flask, request, jsonify, abort, render_template, url_for, redirect
from models import db, MovieModel

# Create Flask app, configure SQLite DB, connect SQLALchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# The HTML Views ____________________________________________________________
@app.route('/')
def home_redirect():
    return render_template('main.html')

@app.route('/main')
def view_main_page():
    return redirect(url_for('view_main_page'))

# Fetching all movies from DB and passing to the index.html template
@app.route('/movies')
def view_all_movies():
    movies = MovieModel.query.order_by(MovieModel.id.asc()).all()
    return render_template('index.html', movies=movies)

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
@app.route('/movies/<int:movie_id>/like', methods=['POST'])
def like_movie(movie_id):
    movie = MovieModel.query.get_or_404(movie_id)
    movie.likes += 1
    db.session.commit()
    return redirect(url_for('movie_detail', movie_id=movie_id))

@app.route('/movies/<int:movie_id>/dislike', methods=['POST'])
def dislike_movie(movie_id):
    movie = MovieModel.query.get_or_404(movie_id)
    movie.dislikes += 1
    db.session.commit()
    return redirect(url_for('movie_detail', movie_id=movie_id))

@app.route('/movies/<int:movie_id>/rate', methods=['POST'])
def rate_movie(movie_id):
    rating = int(request.form['rating'])
    movie = MovieModel.query.get_or_404(movie_id)
    if 1 <= rating <= 5:
        movie.average_rating = ((movie.average_rating * movie.rating_count) + rating) / (movie.rating_count + 1)
        movie.rating_count += 1
        db.session.commit()
    return redirect(url_for('movie_detail', movie_id=movie_id))

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
