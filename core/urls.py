
from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.views.decorators.csrf import ensure_csrf_cookie

from .views import UserView, HomeView, login_view, logout_view
from .views import get_nearby_places, check_in, ping_view, get_user_details
from .views import get_nearby_people, get_notification

userview = ensure_csrf_cookie(UserView.as_view())
homeview = ensure_csrf_cookie(HomeView.as_view())

urlpatterns = patterns('',
    # Homepage
    url(r'^$', homeview, name='five-home'),

    # e.g., nearby/70.92,10.05/
    url(r'^nearby/(?P<lat>[0-9\.]+),(?P<lon>[0-9\.]+)/?$', get_nearby_places,
        name='five-nearby-places'),
    
    url(r'^who/?$', get_nearby_people, name='five-nearby-people'),

    url(r'^checkin/(?P<place_id>[a-zA-Z0-9]+)/?$', check_in, name='five-checkin'),

    url(r'^login/?$', login_view, name='five-login'),

    url(r'^logout/?$', logout_view, name='five-logout'),

    url(r'^ping/(?P<data>.*)/$', ping_view, name='five-ping'),

    url(r'^details/?$', get_user_details, name='five-user-details'),

    url(r'^me/?$', get_user_details, name='five-user-details'),

    # POST API endpoint for creating a user.
    url(r'^user/?$', userview, name='five-create-user'),

    # GET/PUT/DELETE API endpoint for a particular user.
    url(r'^user/(?P<uid>\d+)/?$', userview, name='five-get-user'),

    url(r'^notifyme/?$', get_notification, name='five-get-notification'),

)
