#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from datetime import time
import datetime
import json
import dateutil.parser
from flask.globals import session
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate 
import datetime
from sqlalchemy.exc import OperationalError, ProgrammingError
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
app.config.from_object('config')
migrate=Migrate(app,db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

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
def __repr__(self):
    return f'<Venue {self.id} {self.name} {self.city} {self.state} {self.address} {self.phone} {self.genres} {self.image_link} {self.facebook_link} {self.website_link} {self.seeking_description} {self.num_upcoming_shows} {self.seeking_talent} {self.past_shows}>'
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
  



#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  venuesDistinct=db.session.query(Venue.city.distinct().label('city'),Venue.state.label('state'))
  data=Venue.query.all()
    
  return render_template('pages/venues.html', data=data , venuesDistinct=venuesDistinct)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  response1=Venue.query.filter(Venue.name.ilike('%{}%'.format(request.form.get('search_term', '')))).all()
  for i in response1:
    response={
    "count": len(response1),
    "data": []
    }
  for venue in response1:
    response["data"].append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": venue.num_upcoming_shows
      })
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>',methods=['GET'])
def show_venue(venue_id):

  data1 = Venue.query.get(venue_id)
  showinfo=data1.shows
  past_shows = []
  upcoming_shows = []
  for show in showinfo:
    show_info = {
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": str(show.start_time)
    }
    if(show.start_time>str(datetime.datetime.now())):
      upcoming_shows.append(show_info)
    else:
      past_shows.append(show_info)
  data={
    "name":data1.name,
     "id":data1.id,
    "city":data1.city,
    "state":data1.state,
    "address":data1.address,
    "phone":data1.phone,
    "genres":data1.genres.split(',') ,
     "image_link":data1.image_link,
      "facebook_link":data1.facebook_link ,
       "website_link":data1.website_link,
      "seeking_description":data1.seeking_description,
      "num_upcoming_shows":upcoming_shows,
      "seeking_talent":data1.seeking_talent,
     "past_shows":past_shows,
      "show":data1.shows,
    "past_shows_count": len(past_shows),  
    "upcoming_shows_count": len(upcoming_shows)

      }
    
  return render_template('pages/show_venue.html', venue=data )

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  venue = Venue()

  try:
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.phone = request.form['phone']
    venue.genres = request.form.getlist('genres')
    venue.facebook_link = request.form['facebook_link']
    venue.image_link = request.form['image_link']
    venue.website_link = request.form['website_link']
    setTrue = request.form['seeking_talent']
    if setTrue !=None:
      venue.seeking_talent=True
    else:
      venue.seeking_talent=False
    venue.seeking_description = request.form['seeking_description']
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    print(sys.exc_info())
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
    flash('Venue was successfully deleted!')
  except:
    db.session.rollback()
    flash('Venue was could not be deleted!')
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data=Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  response1=Artist.query.filter(Artist.name.ilike('%{}%'.format(request.form.get('search_term', '')))).all()
  response={
    "count": len(response1),
    "data": []
  }
  for i in response1:
    response["data"].append({
      "id": i.id,
      "name": i.name,
      "num_upcoming_shows":i.upcoming_shows,
    })
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  data1=Artist.query.get(artist_id)
  showinfo=data1.shows
  past_shows = []
  upcoming_shows = []
  for show in showinfo:
    show_info = {
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": str(show.start_time)
    }
    if(show.start_time>str(datetime.datetime.now())):
      upcoming_shows.append(show_info)
    else:
      past_shows.append(show_info)
  data ={
    "id":data1.id,
    "name": data1.name,
    "genres": data1.genres.split(','),
    "city": data1.city,
    "state": data1.state,
    "phone": data1.phone,
    "website": data1.website_link,
    "facebook_link": data1.facebook_link,
    "seeking_venue": data1.seeking_venue,
    "seeking_description": data1.seeking_description,
    "image_link": data1.image_link,
    "show":data1.shows,
    "past_shows":past_shows,
    "upcoming_shows":upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
    }
  return render_template('pages/show_artist.html', artist=data,shows=showinfo)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artists=Artist.query.get(artist_id)
  artist={
    "id": artists.id,
    "name": artists.name,
    "genres": artists.genres.split(','),
    "city": artists.city,
    "state": artists.state,
    "phone": artists.phone,
    "website": artists.website_link,
    "facebook_link": artists.facebook_link,
    "seeking_venue": artists.seeking_venue,
    "seeking_description":artists.seeking_description,
    "image_link": artists.image_link
  }
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist_info=Artist.query.get(artist_id)
  artist_info.name=request.form['name']
  artist_info.genres=request.form.getlist('genres')
  artist_info.city=request.form['city']
  artist_info.state=request.form['state']
  artist_info.phone=request.form['phone']
  artist_info.website_link=request.form['website']
  artist_info.facebook_link=request.form['facebook_link']
  isSet=request.form['seeking_venue']
  if isSet !=None:
    artist_info.seeking_venue=True
  else:
    artist_info.seeking_venue=False
  artist_info.seeking_description=request.form['seeking_description']
  artist_info.image_link=request.form['image_link']
  try:
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully updated!')
  except:
    db.session.rollback()
    flash('Artist ' + request.form['name'] + ' could not be updated!')
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venues=Venue.query.get(venue_id)
  venue={
    "id": venues.id,
    "name": venues.name,
    "genres": venues.genres.split(','),
    "address": venues.address,
    "city": venues.city,
    "state": venues.state,
    "phone": venues.phone,
    "website": venues.website_link,
    "facebook_link": venues.facebook_link,
    "seeking_talent": venues.seeking_talent,
    "seeking_description": venues.seeking_description,
    "image_link": venues.image_link
  }
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  update_venue=Venue.query.get(venue_id)
  if request.method == "POST":
    update_venue.name=request.form['name']
    update_venue.genres=request.form.getlist('genres')
    update_venue.address=request.form['address']
    update_venue.city=request.form['city']
    update_venue.state=request.form['state']
    update_venue.phone=request.form['phone']
    update_venue.website_link=request.form['website_link']
    update_venue.image_link=request.form['image_link']
    update_venue.facebook_link=request.form['facebook_link']
    update_venue.seeking_description=request.form['seeking_description']
    setTrue=request.form['seeking_talent']
    if setTrue !=None:
      update_venue.seeking_talent=True
    else:
      update_venue.seeking_talent=False
  try:
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully updated!')
  except:
     db.session.rollback()
     flash('Venue ' + request.form['name'] + ' could not be updated!')
  finally:
    db.session.close()



  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  artist=Artist()
  try:
        artist.name=request.form['name']
        artist.city=request.form['city']
        artist.state=request.form['state']
        artist.phone=request.form['phone']
        artist.genres=request.form['genres']
        artist.facebook_link=request.form['facebook_link']
        artist.image_link=request.form['image_link']
        artist.website_link=request.form['website_link']
        setTrue=request.form['seeking_venue']
        if setTrue !=None:
          artist.seeking_venue=True
        else:
          artist.seeking_venue=False
        artist.seeking_description=request.form['seeking_description']
        db.session.add(artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
        db.session.rollback()
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
        print(sys.exc_info())
  finally:
        db.session.close()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  showItems=Show.query.all()
  data=[]
  for show in showItems:
      data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": str(show.start_time)
      })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  new_show=Show()
  try:
      new_show.artist_id=request.form['artist_id']
      new_show.venue_id=request.form['venue_id']
      new_show.start_time=request.form['start_time']
      db.session.add(new_show)
      db.session.commit()
      flash('Show was successfully listed!')
  except:
        db.session.rollback()
        flash('An error occurred. Show could not be listed!')
  finally:
        db.session.close()
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
