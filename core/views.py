import json
import random
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic import View, TemplateView
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from .forms import UserCreationForm
from .places import nearby_search
from .models import Place, UserProfile, Notification
from .utilities import random_password, json_response, to_dict, get_post_data
from .utilities import http_basic_auth



@require_http_methods(['POST'])
def logout_view(request):
    logout(request)
    if request.is_ajax():
        return json_response({'success': True})
    return redirect('five-home')


@require_http_methods(['POST'])
@csrf_exempt
def login_view(request):
    '''
    Log our user in.
    
    '''
    data = get_post_data(request)
    error = None
    try:
        username = data['handle']
        password = data['password']
    except KeyError:
        error = 'Incorrect handle/password'
    else:
        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            login(request, user)
        else:
            error = 'Incorrect handle/password'
    if error is not None:
        if request.is_ajax():
            return json_response({'error': error}, 403)
        messages.add_message(request, messages.ERROR, error)
    if request.is_ajax():
        return json_response({'status': 'ok'})
    return redirect('five-home')


@require_http_methods(['POST'])
@login_required
@ensure_csrf_cookie
def check_in(request, place_id):
    '''
    Check the current user in to the place with ID ``place_id``.

    '''
    try:
        place = Place.objects.get(id=place_id)
    except Place.DoesNotExist:
        ret = ({'error': 'No place with id {} found'.format(place_id)}, 404)
    except Exception as e:
        ret = ({'error': str(e)}, 500)
    else:
        profile = request.user.userprofile
        profile.current_location = place
        profile.save()

        # Build notifications for people at this location.
        nearby_profiles = UserProfile.objects.filter(current_location=place).exclude(user=request.user)
        for profile in nearby_profiles:
            Notification.objects.create(user=profile.user, data=json.dumps({
                'image': profile.avatar_url(),
                'data': '{} is around you. Go say hi!'.format(profile.user.username)
            }))
        ret = ({'success': True}, 200)

    return json_response(*ret)


@require_http_methods(['GET'])
@http_basic_auth
@ensure_csrf_cookie
def get_user_details(request):
    '''
    Return the details of the currently logged in User.
    
    '''
    u = request.user
    if u.is_authenticated():
        return json_response(u.userprofile.serialize())
    return json_response({'error': 'login required'}, 403)


@require_http_methods(['GET'])
@http_basic_auth
@ensure_csrf_cookie
def get_nearby_people(request):
    '''
    Return a list of nearby people.

    '''
    current_profile = request.user.userprofile
    ret = current_profile.nearby_people()
    return json_response({'data': [u.serialize() for u in ret]})


@require_http_methods(['POST'])
@http_basic_auth
@login_required
def get_nearby_places(request, lat, lon, rad=1000):
    '''
    Return nearby places centered around a location of
    (lat, lon) and within a radius of ``rad`` metres.

    '''
    data = nearby_search((lat, lon), rad)
    if data['status'] != 'OK':
        try:
            # This is not guaranteed to be present.
            err_msg = data['error_message']
        except KeyError:
            err_msg = 'An error occurred. Try again later'
        return json_response({'error': err_msg})
    places= []
    for result in data['results']:
        result_name = result.get('name')
        if result_name is None:
            # No point in bothering with a place which we don't
            # know the name of.
            continue
        result_loc = result['geometry']['location']
        defaults = {
            'name': result_name,
            'description': '',
            'lat': result_loc['lat'],
            'lon': result_loc['lng'],
            'icon': result['icon'],
        }
        try:
            viewport = result['geometry']['viewport']
            viewport_ne = viewport['northeast']
            viewport_sw = viewport['southwest']
        except KeyError:
            viewport = None
        # Fill in viewport info if we have it
        if viewport is not None:
            defaults.update({
                'viewport_ne_lat': viewport_ne['lat'],
                'viewport_ne_lon': viewport_ne['lng'],
                'viewport_sw_lat': viewport_sw['lat'],
                'viewport_sw_lon': viewport_sw['lng']
            })
        # Store the result in our database if it does not exist
        # already.
        place, created = Place.objects.get_or_create(
            id=result['id'],
            defaults=defaults
        )
        places.append(place)
    resp = {'data': [place.to_dict() for place in places]}
    return json_response(resp)


class HomeView(View):
    def get(self, request):
        if self.request.user.is_authenticated():
            return render(request, 'core/home.html')
        return render(request, 'core/index.html')

    def get_context_data(self, **kwargs):
        return {}


class UserView(View):
    def get(self, request, uid=None):
        '''
        Get info about a user. For an AJAX request, send the JSON
        representation of a user. For a non-AJAX request, render the requested
        user profile

        '''
        if uid is None:
            return json_response({'error': 'No id given'}, status=400)
        try:
            user = User.objects.get(id=uid)
        except User.DoesNotExist:
            return json_response({'error': 'No such user'}, status=404)
        if request.is_ajax():
            return json_response(to_dict(user))
        # Render the user page here
        return render(request, 'core/user.html', {'user': user})

    def post(self, request):
        '''
        Create a new user(Sign up).

        '''
        errors = {}
        data = get_post_data(request)

        # Validate the data
        form = UserCreationForm(data)
        if form.is_valid():
            username = data['handle']
            email = data['email']
            password = data['password']

            # Create the user
            try:
                user = User.objects.create(username=username, email=email)
                user.set_password(password)
                user.save()
            except IntegrityError:
                errors = {'error': 'Error creating user'}
            else:
                UserProfile.objects.create(user=user, bio='')
        else:
            errors = form.errors

        if request.is_ajax():
            if error is not None:
                response = {'status': 'ok', 'id': user.id}
            else:
                response = errors
            return json_response(response)

        if not errors:
            # Log the user in
            user = authenticate(username=username, password=password)
            login(request, user)
        else:
            for item in errors.iteritems():
                messages.add_message(request, messages.ERROR, ':'.join(item))
        # Redirect to home
        return redirect('five-home')


@csrf_exempt
def ping_view(request, data):
    '''
    Simple ping view for debugging.

    '''
    payload = ''
    if request.method == 'POST':
        payload = request.body
    message = data
    return json_response({'message': message, 'payload': payload})


ALPHABET = 'abcdefghijklmnopqrstuvwxyz '

@require_http_methods(['POST'])
@http_basic_auth
@ensure_csrf_cookie
def get_notification(request):
    '''
    Return a notification with some content with a 40% chance.

    '''
    all_notifs = Notification.objects.filter(user=request.user)
    data = [json.loads(notif.data) for notif in all_notifs]
    all_notifs.delete()
    return json_response({'data': data})


