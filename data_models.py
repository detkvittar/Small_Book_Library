from database import db


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=True)
    date_of_death = db.Column(db.Date, nullable=True)

    def __repr__(self):
        return (f"<Author(id='{self.id}', name='{self.name}', "
                f"birth_date='{self.birth_date}', "
                f"date_of_death='{self.date_of_death}')>")

    def __str__(self):
        return (f"Author: {self.name} (Born: {self.birth_date}, "
                f"Died: {self.date_of_death})")


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(13), nullable=False, unique=True)
    title = db.Column(db.String(200), nullable=False)
    publication_year = db.Column(db.Integer, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)

    author = db.relationship('Author', backref=db.backref('books', lazy=True))

    def __repr__(self):
        return (f"<Book(id='{self.id}', isbn='{self.isbn}', title='{self.title}', "
                f"publication_year='{self.publication_year}', "
                f"author_id='{self.author_id}')>")

    def __str__(self):
        return (f"Book: {self.title} (ISBN: {self.isbn}, "
                f"Published: {self.publication_year})")
