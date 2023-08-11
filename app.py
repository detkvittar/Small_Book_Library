from flask import Flask, render_template, request, redirect, url_for, flash
import requests
import os
from datetime import datetime
from sqlalchemy import func
from database import db
from data_models import Book, Author


app = Flask(__name__)
db_path = os.path.abspath("instance/library.db")
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SECRET_KEY'] = 'hardcodedyo'

db.init_app(app)


@app.route('/')
@app.route('/home', methods=['GET'])
def homepage():
    search_query = request.args.get('search')
    sort_by = request.args.get('sort_by', 'title')
    books = []

    if search_query:
        books_query = Book.query.filter(Book.title.ilike(f'%{search_query}%'))
    else:
        books_query = Book.query

    if sort_by == 'title':
        books = books_query.join(Author).order_by(
            func.lower(Book.title), func.lower(Author.name)).all()
    elif sort_by == 'author':
        books = books_query.join(Author).order_by(
            func.lower(Author.name), func.lower(Book.title)).all()

    for book in books:
        response = requests.get(
            f"http://covers.openlibrary.org/b/isbn/{book.isbn}-L.jpg")
        if response.status_code == 200:
            book.cover_url = f"http://covers.openlibrary.org/b/isbn/{book.isbn}-L.jpg"
        else:
            book.cover_url = None

    return render_template('home.html', books=books, sort_by=sort_by, search_query=search_query or '')


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    if request.method == 'POST':
        name = request.form.get('name')
        birthdate = datetime.strptime(
            request.form.get('birthdate'), '%Y-%m-%d').date()
        date_of_death_str = request.form.get('date_of_death')
        date_of_death = datetime.strptime(
            date_of_death_str, '%Y-%m-%d').date() if date_of_death_str else None

        author = Author(name=name, birth_date=birthdate,
                        date_of_death=date_of_death)

        db.session.add(author)
        db.session.commit()

        flash('Author added successfully!')
        return redirect(url_for('add_author'))

    return render_template('add_author.html')


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        isbn = request.form.get('isbn')
        title = request.form.get('title')
        publication_year = int(request.form.get('publication_year'))
        author_id = int(request.form.get('author_id'))

        book = Book(isbn=isbn, title=title,
                    publication_year=publication_year, author_id=author_id)

        db.session.add(book)
        db.session.commit()

        flash('Book added successfully!')
        return redirect(url_for('add_book'))

    authors = Author.query.all()
    return render_template('add_book.html', authors=authors)


@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()

    remaining_books_with_author = Book.query.filter_by(
        author_id=book.author_id).all()
    if not remaining_books_with_author:
        author = Author.query.get(book.author_id)
        db.session.delete(author)
        db.session.commit()

    flash('Book deleted successfully!')
    return redirect(url_for('homepage'))


app.run(debug=True, host='0.0.0.0')
