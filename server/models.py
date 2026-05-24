from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin

db = SQLAlchemy()

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)

    # Establish clean relationships
    articles = db.relationship('Article', back_populates='user', cascade='all, delete-orphan')
    
    # Simple serialization rule preventing recursion loops
    serialize_rules = ('-articles.user',)


class Article(db.Model, SerializerMixin):
    __tablename__ = 'articles'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.String, nullable=False)
    preview = db.Column(db.String)
    minutes_to_read = db.Column(db.Integer)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    user = db.relationship('User', back_populates='articles')
    serialize_rules = ('-user.articles',)

