import json
import requests
from django.conf import settings

API_KEY = settings.GOOGLE_PLACES_API_KEY


NEARBY_SEARCH_URL = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'


OUR_LOC = (18.5549023, 73.92374939999999)

def nearby_search(loc, rad):
    '''
    Get the Google places API result for a places within radius ``rad`` of the
    location ``loc``, which is of the form (lat, lon)
        
    '''
    print loc
    params = {
        'key': API_KEY,
        'location': '{},{}'.format(*loc),
        'sensor': 'true',
        'rankby': 'distance',
        # TODO: add additional types here
        'types': 'finance|cafe|movie_theater|health|book_store|electronics_store|'
                 'gym|night_club'

    }
    response = requests.get(NEARBY_SEARCH_URL, params=params)
    return response.json()

