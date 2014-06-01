import urlparse
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


class Place(models.Model):
    '''
    A place to check in to.

    '''
    # The id of this place as returned by the Google Places API
    id = models.TextField(primary_key=True)
    name = models.TextField()
    description = models.TextField()

    # Location info
    lat = models.FloatField()
    lon = models.FloatField()

    # A URL to the icon to be displayed for this place, as
    # returned by the Google Places API.
    icon = models.URLField()
    
    # The lat/lon of the North-East corner of this place's viewport
    viewport_ne_lat = models.FloatField(null=True)
    viewport_ne_lon = models.FloatField(null=True)

    # The lat/lon of the South-West corner of this place's viewport
    viewport_sw_lat = models.FloatField(null=True)
    viewport_sw_lon = models.FloatField(null=True)

    def people(self):
        '''
        Return a list(like object) of profiles of users in this place.

        '''
        return self.userprofile_set.all()

    def viewport(self):
        '''
        Get the viewport for this place.

        '''
        viewport_given = (self.viewport_ne_lat is None or
                          self.viewport_ne_lon is None or
                          self.viewport_sw_lat is None or 
                          self.viewport_sw_lon is None)
        if viewport_given:
            return {
                'northeast': {
                    'lat': self.viewport_ne_lat,
                    'lon': self.viewport_ne_lon
                },
                'southwest': {
                    'lat': self.viewport_sw_lat,
                    'lon': self.viewport_sw_lon
                }
            }

        return None

    def __unicode__(self):
        return self.name

    def __contains__(self, location):
        '''
        Check if ``location`` falls within this place. ``location`` is a 
        tuple of the form (lat, lon)

        Usage:

            if (41.55, 77.34) in place:
                ...

        '''
        if self.viewport() is None:
            # If we were not given a viewport, just check for exact equality
            return location == (self.lat, self.lon)
        lat, lon = location
        # This approximates the situation ignoring geodesic geometry; Should
        # be good enough for most places worth checking in, but might fail
        # when dealing with HUGE places.
        return (self.viewport_sw_lat <= lat <= self.viewport_ne_lat and
                self.viewport_sw_lon <= lon <= self.viewport_ne_lon)

    def to_dict(self):
        '''
        Return a dictionary representation of this place.

        '''
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'location': {
                'lat': self.lat,
                'lon': self.lon
            },
            'icon': self.icon
        }

    def serialize(self, detailed=False):
        '''
        Return a JSON encodable Python representation.
        
        '''
        ret = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon
        }

        # Insert the lat and lon for a detailed repr
        if detailed: 
            ret['location'] = {'lat': self.lat, 'lon': self.lon}

        return ret


class Interest(models.Model):
    '''
    A user interest.

    '''
    name = models.TextField()

    def serialize(self, detailed=False):
        '''
        Return a JSON encodable Python representation.
        
        '''
        return {'id': self.id, 'name': self.name}


class UserProfile(models.Model):
    '''
    Information about a user apart from their login creds.

    '''
    user = models.OneToOneField(User, primary_key=True)

    # A short bio.
    bio = models.CharField(max_length=120, blank=True)

    # Other user profiles this user profile is connected to.
    connections = models.ManyToManyField('self', null=True, blank=True)

    current_location = models.ForeignKey(Place, null=True, blank=True)

    interests = models.ManyToManyField(Interest, null=True, blank=True)

    meet_new_people = models.BooleanField(default=True)

    def nearby_people(self):
        '''
        Get a list(like object) of people checked into the same place as this
        one.

        '''
        if self.current_location is None:
            return []
        return self.current_location.userprofile_set.exclude(user=self.user)

    def avatar_url(self):
        '''
        Get the relative URL of this user's avatar.

        '''
        return urlparse.urljoin(settings.STATIC_URL,
                                'core/img/{}.png'.format(self.user.id))

    def serialize(self, detailed=False):
        '''
        Return a JSON encodable Python representation.
        
        '''
        ret = {
            'id': self.user.id,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'handle': self.user.username,
            'bio': self.bio,
            'interests': [intr.serialize(detailed) for intr in self.interests.all()],
            'meet_new_people': self.meet_new_people,
            'avatar': self.avatar_url()
        }

        if detailed:
            ret.update({
                'connections': [u.user.id for u in self.connections.all()],
                'current_location': self.current_location.serialize(detailed)
            })

        return ret


class PlacePicture(models.Model):
    '''
    Picture uploaded by a user of a place.

    '''
    path = models.TextField()
    author = models.ForeignKey(UserProfile)
    place = models.ForeignKey(Place)


