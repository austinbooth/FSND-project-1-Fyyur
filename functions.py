#----------------------------------------------------------------------------#
# Custom functions.
#----------------------------------------------------------------------------#
from datetime import datetime
from models import Venue, Artist, Show

def get_shows_by_venue_or_artist(id, find='venue', upcoming=True):
    if find == 'venue':
        shows = Show.query.filter_by(venue_id=id).all()
    elif find == 'artist':
        shows = Show.query.filter_by(artist_id=id).all()

    show_num = 0
    show_ids = []
    for show in shows:
        if upcoming == True: # find future shows
            if show.start_time > datetime.now():
                show_num += 1
                show_ids.append(show.id)
            elif upcoming == False: # find past shows
                if show.start_time < datetime.now():
                    show_num += 1
                    show_ids.append(show.id)

    return show_num, show_ids

def get_info_shows(show_ids, return_data='artist'):
    data = []
    for show_id in show_ids:
        temp = {}
        show = Show.query.get(show_id)

        if return_data == 'artist':
            artist = Artist.query.get(show.artist_id)
            temp = {
                "artist_id": show.artist_id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
            }
        elif return_data == 'venue':
            venue = Venue.query.get(show.venue_id)
            temp = {
                "venue_id": show.venue_id,
                "venue_name": venue.name,
                "venue_image_link": venue.image_link,
                "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
            }
            data.append(temp)
    return data
