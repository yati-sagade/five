import json
import random
from functools import wraps
from django.http import HttpResponse

PASSWORD_APLPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'


def random_password(n=10):
    return ''.join(random.choice(PASSWORD_APLPHABET) for i in xrange(n))


def to_dict(user):
    user_dict = {'handle': user.username, 'email': user.email, 'id': user.id}
    return user_dict


def json_response(obj, status=200):
    return HttpResponse(json.dumps(obj), content_type='application/json; charset=utf-8',
                        status=status)


def get_post_data(request):
    '''
    Get the POST data dict from a HttpRequest

    '''
    if request.is_ajax():
        data = json.loads(request.body)
    else:
        data = request.POST
    return data


def http_basic_auth(func):
    @wraps(func)
    def _decorator(request, *args, **kwargs):
        from django.contrib.auth import authenticate, login
        if request.META.has_key('HTTP_AUTHORIZATION'):
            authmeth, auth = request.META['HTTP_AUTHORIZATION'].split(' ', 1)
            if authmeth.lower() == 'basic':
                auth = auth.strip().decode('base64')
                username, password = auth.split(':', 1)
                user = authenticate(username=username, password=password)
                if user:
                    login(request, user)
        return func(request, *args, **kwargs)
    return _decorator

