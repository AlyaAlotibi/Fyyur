from flask import Flask
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    genres=db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    website_link=db.Column(db.String(120))
    seeking_talent=db.Column(db.Boolean,default=False)
    shows=db.relationship('Show',backref='venue',lazy=True)
    seeking_description=db.Column(db.String(120))
    num_upcoming_shows=db.Column(db.Integer)
    past_shows=db.Column(db.Integer)
class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link= db.Column(db.String(120))
    seeking_venue=db.Column(db.Boolean,default=False)
    seeking_description=db.Column(db.String(120))
    shows=db.relationship('Show',backref='artist',lazy=True)
    upcoming_shows=db.Column(db.Integer)
    past_shows=db.Column(db.Integer)

class Show(db.Model):
  __tablename__ = 'Show'
  id=db.Column(db.Integer,primary_key=True)
  start_time=db.Column(db.DateTime)
  venue_id=db.Column(db.Integer,db.ForeignKey('Venue.id'))
  artist_id=db.Column(db.Integer,db.ForeignKey('Artist.id'))