#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import logging
from logging import Formatter, FileHandler
from datetime import datetime
import sys
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import Form

# Now app files
from forms import *
from models import db, Venue, Artist, Show
from functions import get_shows_by_venue_or_artist, get_info_shows

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
#db = SQLAlchemy(app)

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Custom functions.
#----------------------------------------------------------------------------#

# def get_shows_by_venue_or_artist(id, find='venue', upcoming=True):
#     if find == 'venue':
#         shows = Show.query.filter_by(venue_id=id).all()
#     elif find == 'artist':
#         shows = Show.query.filter_by(artist_id=id).all()

#     show_num = 0
#     show_ids = []
#     for show in shows:
#         if upcoming == True: # find future shows
#             if show.start_time > datetime.now():
#                 show_num += 1
#                 show_ids.append(show.id)
#             elif upcoming == False: # find past shows
#                 if show.start_time < datetime.now():
#                     show_num += 1
#                     show_ids.append(show.id)

#     return show_num, show_ids

# def get_info_shows(show_ids, return_data='artist'):
#     data = []
#     for show_id in show_ids:
#         temp = {}
#         show = Show.query.get(show_id)

#         if return_data == 'artist':
#             artist = Artist.query.get(show.artist_id)
#             temp = {
#                 "artist_id": show.artist_id,
#                 "artist_name": artist.name,
#                 "artist_image_link": artist.image_link,
#                 "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
#             }
#         elif return_data == 'venue':
#             venue = Venue.query.get(show.venue_id)
#             temp = {
#                 "venue_id": show.venue_id,
#                 "venue_name": venue.name,
#                 "venue_image_link": venue.image_link,
#                 "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
#             }
#             data.append(temp)
#     return data

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
    # TODO: replace with real venues data. - DONE
    #       num_shows should be aggregated based on number of upcoming shows per venue. - DONE
    # data=[{
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "venues": [{
    #     "id": 1,
    #     "name": "The Musical Hop",
    #     "num_upcoming_shows": 0,
    #     }, {
    #     "id": 3,
    #     "name": "Park Square Live Music & Coffee",
    #     "num_upcoming_shows": 1,
    #     }]
    # }, {
    #     "city": "New York",
    #     "state": "NY",
    #     "venues": [{
    #     "id": 2,
    #     "name": "The Dueling Pianos Bar",
    #     "num_upcoming_shows": 0,
    #     }]
    # }]

    data2 = Venue.query.order_by(Venue.state, Venue.city).all()
    data = []
    cities = []
    last_city = ''
    last_state = ''

    for item in data2:
        temp = {}
        num_upcoming, upcoming_ids = get_shows_by_venue_or_artist(item.id, find='venue', upcoming=True)
        venue = {'id': item.id, 'name': item.name, "num_upcoming_shows": num_upcoming}

        if (last_state != item.state and last_city != item.city):
            temp['city'] = item.city
            temp['state'] = item.state
            temp['venues'] = [venue]
            data.append(temp)
        else:
            temp = data.pop()
            temp['venues'].append(venue)
            data.append(temp)

            last_state = item.state
            last_city = item.city

    print(data)
    return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive. - DONE
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    response={
        "count": 1,
        "data": [{
        "id": 2,
        "name": "The Dueling Pianos Bar",
        "num_upcoming_shows": 0,
        }]
    }

    search_term = request.form.get('search_term')
    venues = Venue.query.filter(Venue.name.ilike('%' + search_term + '%'))

    response = {}
    count = 0
    data = []

    for venue in venues:
        temp = {}
        count += 1

        temp['id'] = venue.id
        temp['name'] = venue.name
        num_upcoming, upcoming_ids = get_shows_by_venue_or_artist(venue.id, find='venue', upcoming=True)
        temp['num_upcoming_shows'] = num_upcoming

        data.append(temp)

    if count == 0:
        response = {
            "count": 0,
            "data": []
        }
    else:
        response = {
            "count": count,
            "data": data
        }

    print('*** ', response)
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id - DONE
    # data1={
    #   "id": 1,
    #   "name": "The Musical Hop",
    #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    #   "address": "1015 Folsom Street",
    #   "city": "San Francisco",
    #   "state": "CA",
    #   "phone": "123-123-1234",
    #   "website": "https://www.themusicalhop.com",
    #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
    #   "seeking_talent": True,
    #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    #   "past_shows": [{
    #     "artist_id": 4,
    #     "artist_name": "Guns N Petals",
    #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #     "start_time": "2019-05-21T21:30:00.000Z"
    #   }],
    #   "upcoming_shows": [],
    #   "past_shows_count": 1,
    #   "upcoming_shows_count": 0,
    # }
    # data2={
    #   "id": 2,
    #   "name": "The Dueling Pianos Bar",
    #   "genres": ["Classical", "R&B", "Hip-Hop"],
    #   "address": "335 Delancey Street",
    #   "city": "New York",
    #   "state": "NY",
    #   "phone": "914-003-1132",
    #   "website": "https://www.theduelingpianos.com",
    #   "facebook_link": "https://www.facebook.com/theduelingpianos",
    #   "seeking_talent": False,
    #   "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    #   "past_shows": [],
    #   "upcoming_shows": [],
    #   "past_shows_count": 0,
    #   "upcoming_shows_count": 0,
    # }
    # data3={
    #   "id": 3,
    #   "name": "Park Square Live Music & Coffee",
    #   "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    #   "address": "34 Whiskey Moore Ave",
    #   "city": "San Francisco",
    #   "state": "CA",
    #   "phone": "415-000-1234",
    #   "website": "https://www.parksquarelivemusicandcoffee.com",
    #   "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    #   "seeking_talent": False,
    #   "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #   "past_shows": [{
    #     "artist_id": 5,
    #     "artist_name": "Matt Quevedo",
    #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #     "start_time": "2019-06-15T23:00:00.000Z"
    #   }],
    #   "upcoming_shows": [{
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-01T20:00:00.000Z"
    #   }, {
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-08T20:00:00.000Z"
    #   }, {
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-15T20:00:00.000Z"
    #   }],
    #   "past_shows_count": 1,
    #   "upcoming_shows_count": 1,
    # }
    #data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]

    venue = Venue.query.get(venue_id)
    data = {
        'id': venue_id,
        'name': venue.name,
        'genres': venue.genres.replace('{', '').replace('}', '').replace('\"', '').split(','),
        'address': venue.address,
        'city': venue.city,
        'state': venue.state,
        'phone': venue.phone,
        'website': venue.website,
        'facebook_link': venue.facebook_link,
        'image_link': venue.image_link,
        'seeking_talent': venue.seeking_talent
    }
    if venue.seeking_description != '':
        data['seeking_description'] = venue.seeking_description

    num_upcoming_shows, upcoming_show_ids = get_shows_by_venue_or_artist(venue_id, find='venue', upcoming=True)
    num_past_shows, past_show_ids = get_shows_by_venue_or_artist(venue_id, find='venue', upcoming=False)

    print('****************************************************************************')
    print('Upcoming no: ', num_upcoming_shows)
    print('Upcoming ids: ', upcoming_show_ids)
    print('------------------------------------')
    print('Past no: ', num_past_shows)
    print('Past ids: ', past_show_ids)
    print('****************************************************************************')
    print('Genres: ', venue.genres.split(','))

    data['past_shows'] = get_info_shows(past_show_ids)
    data['upcoming_shows'] = get_info_shows(upcoming_show_ids)

    data['past_shows_count'] = num_past_shows
    data['upcoming_shows_count'] = num_upcoming_shows

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead - DONE
    # TODO: modify data to be the data object returned from db insertion - IGNORE

    form = VenueForm(request.form)
    if form.validate_on_submit():
        error = False
        try:
            name = request.form.get('name')
            city = request.form.get('city')
            state = request.form.get('state')
            address = request.form.get('address')
            phone = request.form.get('phone')
            genres = request.form.getlist('genres')
            image_link = "".join(request.form.getlist('image_link')) # Here join is being used to convert the list returned to a string
            website = "".join(request.form.getlist('website'))
            fb_link = request.form.get('facebook_link')

            if request.form.get('seeking_talent') == 'Yes':
                seeking_talent = True
            else:
                seeking_talent = False

            seeking_description = "".join(request.form.getlist('seeking_description'))

            venue = Venue(
                name=name,
                city=city,
                state=state,
                address=address,
                phone=phone,
                genres=genres,
                image_link=image_link,
                website=website,
                facebook_link=fb_link,
                seeking_talent=seeking_talent,
                seeking_description=seeking_description
            )

            db.session.add(venue)
            db.session.commit()

        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
        if not error:
            # on successful db insert, flash success
            flash('Venue ' + request.form['name'] + ' was successfully listed!')
            return render_template('pages/home.html')
        else:
            flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
            abort(500)
    else:
        print('*** Issue in validation.')
        print(form.validate_on_submit())
        print(form.errors)
        flash('Creation of venue ' + request.form['name'] + ' failed due to a validation error. Please try again.')
        return render_template('pages/home.html')

    # TODO: on unsuccessful db insert, flash an error instead. - DONE
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
 

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using - DONE
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        Show.query.filter_by(venue_id=venue_id).delete()
        venue = Venue.query.get(venue_id)
        venue_name = venue.name
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return None
    #return jsonify({ 'success': True })

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database - DONE

    data=[{
        "id": 4,
        "name": "Guns N Petals",
    }, {
        "id": 5,
        "name": "Matt Quevedo",
    }, {
        "id": 6,
        "name": "The Wild Sax Band",
    }]

    artists = Artist.query.all()
    data = []
    for artist in artists:
        temp = {}
        temp['id'] = artist.id
        temp['name'] = artist.name
        data.append(temp)

    return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive. - DONE
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    response={
        "count": 1,
        "data": [{
        "id": 4,
        "name": "Guns N Petals",
        "num_upcoming_shows": 0,
        }]
    }

    search_term = request.form.get('search_term')
    artists = Artist.query.filter(Artist.name.ilike('%' + search_term + '%'))

    response = {}
    count = 0
    data = []

    for artist in artists:
        temp = {}
        count += 1

        temp['id'] = artist.id
        temp['name'] = artist.name
        num_upcoming, upcoming_ids = get_shows_by_venue_or_artist(artist.id, find='artist', upcoming=True)
        temp['num_upcoming_shows'] = num_upcoming

        data.append(temp)

    if count == 0:
        response = {
            "count": 0,
            "data": []
        }
    else:
        response = {
            "count": count,
            "data": data
        }

    print('*** ', response)

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given venue_id
    # TODO: replace with real venue data from the artist table, using id - DONE

    # data1={
    #   "id": 4,
    #   "name": "Guns N Petals",
    #   "genres": ["Rock n Roll"],
    #   "city": "San Francisco",
    #   "state": "CA",
    #   "phone": "326-123-5000",
    #   "website": "https://www.gunsnpetalsband.com",
    #   "facebook_link": "https://www.facebook.com/GunsNPetals",
    #   "seeking_venue": True,
    #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #   "past_shows": [{
    #     "venue_id": 1,
    #     "venue_name": "The Musical Hop",
    #     "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    #     "start_time": "2019-05-21T21:30:00.000Z"
    #   }],
    #   "upcoming_shows": [],
    #   "past_shows_count": 1,
    #   "upcoming_shows_count": 0,
    # }
    # data2={
    #   "id": 5,
    #   "name": "Matt Quevedo",
    #   "genres": ["Jazz"],
    #   "city": "New York",
    #   "state": "NY",
    #   "phone": "300-400-5000",
    #   "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    #   "seeking_venue": False,
    #   "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #   "past_shows": [{
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #     "start_time": "2019-06-15T23:00:00.000Z"
    #   }],
    #   "upcoming_shows": [],
    #   "past_shows_count": 1,
    #   "upcoming_shows_count": 0,
    # }
    # data3={
    #   "id": 6,
    #   "name": "The Wild Sax Band",
    #   "genres": ["Jazz", "Classical"],
    #   "city": "San Francisco",
    #   "state": "CA",
    #   "phone": "432-325-5432",
    #   "seeking_venue": False,
    #   "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #   "past_shows": [],
    #   "upcoming_shows": [{
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #     "start_time": "2035-04-01T20:00:00.000Z"
    #   }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #     "start_time": "2035-04-08T20:00:00.000Z"
    #   }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #     "start_time": "2035-04-15T20:00:00.000Z"
    #   }],
    #   "past_shows_count": 0,
    #   "upcoming_shows_count": 3,
    # }
    # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]

    artist = Artist.query.get(artist_id)
    data = {
        'id': artist_id,
        'name': artist.name,
        'genres': artist.genres.replace('{', '').replace('}', '').replace('\"', '').split(','),
        'city': artist.city,
        'state': artist.state,
        'phone': artist.phone,
        'website': artist.website,
        'facebook_link': artist.facebook_link,
        'image_link': artist.image_link,
        'seeking_venue': artist.seeking_venue
    }
    if artist.seeking_description != '':
        data['seeking_description'] = artist.seeking_description

    num_upcoming_shows, upcoming_show_ids = get_shows_by_venue_or_artist(artist_id, find='artist', upcoming=True)
    num_past_shows, past_show_ids = get_shows_by_venue_or_artist(artist_id, find='artist', upcoming=False)

    print('****************************************************************************')
    print('Upcoming no: ', num_upcoming_shows)
    print('Upcoming ids: ', upcoming_show_ids)
    print('------------------------------------')
    print('Past no: ', num_past_shows)
    print('Past ids: ', past_show_ids)
    print('****************************************************************************')
    print('Genres: ', artist.genres.split(','))

    data['past_shows'] = get_info_shows(past_show_ids, return_data='venue')
    data['upcoming_shows'] = get_info_shows(upcoming_show_ids, return_data='venue')

    data['past_shows_count'] = num_past_shows
    data['upcoming_shows_count'] = num_upcoming_shows

    print('************************************************')
    print(data)
    print('************************************************')


    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    # artist={
    #   "id": 4,
    #   "name": "Guns N Petals",
    #   "genres": ["Rock n Roll"],
    #   "city": "San Francisco",
    #   "state": "CA",
    #   "phone": "326-123-5000",
    #   "website": "https://www.gunsnpetalsband.com",
    #   "facebook_link": "https://www.facebook.com/GunsNPetals",
    #   "seeking_venue": True,
    #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
    # }

    artist = Artist.query.get(artist_id)

    artist_data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link
    }

    artist_genres = artist.genres.replace('{', '').replace('}', '').replace('\"', '').split(',')

    if artist.seeking_venue == True:
        seeking_venue_select = 'Yes'
    else:
        seeking_venue_select = 'No'

    form = ArtistForm(genres=artist_genres, state=artist.state, seeking_venue=seeking_venue_select)
    print('***', artist_genres)
    # TODO: populate form with fields from artist with ID <artist_id> - DONE
    return render_template('forms/edit_artist.html', form=form, artist=artist_data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing - DONE
    # artist record with ID <artist_id> using the new attributes

    form = ArtistForm(request.form)
    if form.validate_on_submit():
        artist = Artist.query.get(artist_id)

        error = False
        try:
            name = request.form.get('name')
            city = request.form.get('city')
            state = request.form.get('state')
            phone = request.form.get('phone')
            genres = request.form.getlist('genres') # note that this returns a list of all selected genres
            fb_link = request.form.get('facebook_link')

            if request.form.get('seeking_venue') == 'Yes':
                seeking_venue = True
            else:
                seeking_venue = False

            seeking_description = request.form.get('seeking_description')
            image_link = request.form.get('image_link')
            website = request.form.get('website')

            artist.name = name
            artist.city = city
            artist.state = state
            artist.phone = phone
            artist.genres = genres
            artist.facebook_link = fb_link
            artist.website = website
            artist.seeking_venue = seeking_venue
            artist.seeking_description = seeking_description
            artist.image_link = image_link

            db.session.add(artist)
            db.session.commit()

        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
        if not error:
            # on successful db insert, flash success
            flash('Artist ' + request.form['name'] + ' was successfully edited!')
            return render_template('pages/home.html')
        else:
            flash('An error occurred. Artist ' + request.form['name'] + ' could not be edited.')
            abort(500)

        #return redirect(url_for('show_artist', artist_id=artist_id))
    else:
        print('*** Issue in validation.')
        print(form.validate_on_submit())
        print(form.errors)
        flash('Editing of artist ' + request.form['name'] + ' failed to add due to a validation error. Please try again.')
        return redirect(url_for('edit_artist', artist_id=artist_id))
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue={
        "id": 1,
        "name": "The Musical Hop",
        "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
        "address": "1015 Folsom Street",
        "city": "San Francisco",
        "state": "CA",
        "phone": "123-123-1234",
        "website": "https://www.themusicalhop.com",
        "facebook_link": "https://www.facebook.com/TheMusicalHop",
        "seeking_talent": True,
        "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
        "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
    }
    # TODO: populate form with values from venue with ID <venue_id> - DONE

    venue = Venue.query.get(venue_id)

    venue_data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link
    }

    venue_genres = venue.genres.replace('{', '').replace('}', '').replace('\"', '').split(',')

    if venue.seeking_talent == True:
        seeking_talent_select = 'Yes'
    else:
        seeking_talent_select = 'No'

    form = VenueForm(genres=venue_genres, state=venue.state, seeking_talent=seeking_talent_select)

    return render_template('forms/edit_venue.html', form=form, venue=venue_data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing - DONE
    # venue record with ID <venue_id> using the new attributes

    form = VenueForm(request.form)
    if form.validate_on_submit():
        venue = Venue.query.get(venue_id)

        error = False
        try:
            name = request.form.get('name')
            city = request.form.get('city')
            state = request.form.get('state')
            address = request.form.get('address')
            phone = request.form.get('phone')
            genres = request.form.getlist('genres') # note that this returns a list of all selected genres
            fb_link = request.form.get('facebook_link')

            if request.form.get('seeking_talent') == 'Yes':
                seeking_talent = True
            else:
                seeking_talent = False

            seeking_description = request.form.get('seeking_description')
            image_link = request.form.get('image_link')
            website = request.form.get('website')

            venue.name = name
            venue.city = city
            venue.state = state
            venue.address = address
            venue.phone = phone
            venue.genres = genres
            venue.facebook_link = fb_link
            venue.website = website
            venue.seeking_talent = seeking_talent
            venue.seeking_description = seeking_description
            venue.image_link = image_link

            db.session.add(venue)
            db.session.commit()

        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
        if not error:
            # on successful db insert, flash success
            flash('Venue ' + request.form['name'] + ' was successfully edited!')
            return render_template('pages/home.html')
        else:
            flash('An error occurred. Venue ' + request.form['name'] + ' could not be edited.')
            abort(500)
    else:
        print('*** Issue in validation.')
        print(form.validate_on_submit())
        print(form.errors)
        flash('Editing of venue ' + request.form['name'] + ' failed to add due to a validation error. Please try again.')
        return redirect(url_for('edit_venue', venue_id=venue_id))
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Artist record in the db, instead - DONE
    # TODO: modify data to be the data object returned from db insertion

    form = ArtistForm(request.form)
    if form.validate_on_submit():
        error = False
        try:
            name = request.form.get('name')
            city = request.form.get('city')
            state = request.form.get('state')
            phone = request.form.get('phone')
            genres = request.form.getlist('genres') # note that this returns a list of all selected genres
            fb_link = request.form.get('facebook_link')

            if request.form.get('seeking_venue') == 'Yes':
                seeking_venue = True
            else:
                seeking_venue = False

            seeking_description = request.form.get('seeking_description')
            image_link = request.form.get('image_link')
            website = request.form.get('website')

            artist = Artist(
                name=name,
                city=city,
                state=state,
                phone=phone,
                genres=genres,
                facebook_link=fb_link,
                website=website,
                seeking_venue=seeking_venue,
                seeking_description=seeking_description,
                image_link=image_link
            )

            db.session.add(artist)
            db.session.commit()
        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
        if not error:
            # on successful db insert, flash success
            flash('Artist ' + request.form['name'] + ' was successfully listed!')
            return render_template('pages/home.html')
        else:
            flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
            abort(500)
    else:
        print('*** Issue in validation.')
        print(form.validate_on_submit())
        print(form.errors)
        flash('Creation of artist ' + request.form['name'] + ' failed to add due to a validation error. Please try again.')
        return render_template('pages/home.html')
    return redirect(url_for('show_artist', artist_id=artist_id))

    # TODO: on unsuccessful db insert, flash an error instead. - DONE


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real shows data. - DONE

    # data=[{
    #     "venue_id": 1,
    #     "venue_name": "The Musical Hop",
    #     "artist_id": 4,
    #     "artist_name": "Guns N Petals",
    #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #     "start_time": "2019-05-21T21:30:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 5,
    #     "artist_name": "Matt Quevedo",
    #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #     "start_time": "2019-06-15T23:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-01T20:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-08T20:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-15T20:00:00.000Z"
    # }]

    shows = Show.query.order_by('start_time').all()
    data = []
    for show in shows:
        temp = {}
        temp['venue_id'] = show.venue_id
        temp['venue_name'] = Venue.query.get(show.venue_id).name
        temp['artist_id'] = show.artist_id
        temp['artist_name'] = Artist.query.get(show.artist_id).name
        temp['artist_image_link'] = Artist.query.get(show.artist_id).image_link
        temp['start_time'] = show.start_time.strftime("%m/%d/%Y, %H:%M:%S")

        data.append(temp)
        print('************ ', temp)

    return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead - DONE
    error = False
    try:
        artist_id = request.form.get('artist_id')
        venue_id = request.form.get('venue_id')
        start_time = request.form.get('start_time')

        show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
        db.session.add(show)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if not error:
        # on successful db insert, flash success
        flash('Show was successfully listed!')
        return render_template('pages/home.html')
    else:
        flash('An error occurred. The Show could not be listed.')
        abort(500)
    # TODO: on unsuccessful db insert, flash an error instead. - DONE
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

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
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
