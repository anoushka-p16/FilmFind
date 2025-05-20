import re
import pandas as pd
from app import app
from models import db, MovieModel

# Handles unknown strings safely
def safe_str(val):
    if pd.isna(val): 
        return "Unknown"
    s = str(val).strip()
    return s if s else "Unknown"

# Handles invalid integers safely
def safe_int(val):
    if pd.isna(val):
        return 0
    s = str(val)
    m = re.search(r'(\d+)', s)
    return int(m.group(1)) if m else 0

# Gets movies from the Excel file and adds to DB
def get_movies(path='topMovies.xlsx'):
    df = pd.read_excel(path, engine='openpyxl')

    with app.app_context():
        for row in df.itertuples(index=False):
            poster   = safe_str(row.Poster)
            title    = safe_str(row.Title)
            year     = safe_int(row.Year)
            rating   = safe_str(row.Rating)
            runtime  = safe_int(row.Runtime)
            genre    = safe_str(row.Genre)
            summary  = safe_str(row.Summary)
            director = safe_str(row.Director)
            actors   = [safe_str(row.Star1),
                        safe_str(row.Star2),
                        safe_str(row.Star3),
                        safe_str(row.Star4)]

            # If movie does not already exist in DB, add it
            if not MovieModel.query.filter_by(title=title, year=year).first():
                movie = MovieModel(
                    poster,
                    title,
                    year,
                    rating,
                    runtime,
                    genre,
                    summary,
                    director,
                    actors
                )
                db.session.add(movie)
        db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    get_movies()
