var core = (function(){
    var obj = {};
    var url = '/nearby';

    obj.getCookie = function(name){
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    };

    obj.getNearByPlaces = function(callback) {
        navigator.geolocation.getCurrentPosition(function(loc){
            alert('in here');
            var lat = loc.coords.latitude,
                lon = loc.coords.longitude;
            $.ajax(url + "/" + lat + "," + lon + "/", {
                success: function(result, status, xhr) {
                    callback(result);
                },
                error: function(result, status, xhr) {
                    callback(result);
                },
                type: 'POST',
                headers: {
                    'X-CSRFToken': obj.getCookie('csrftoken')
                }
            });
        });
    };

    obj.checkin = function(placeId, callback) {
        var postURL = '/checkin/' + placeId + '/';
        $.ajax(postURL, {
            success: function(result, status, xhr) {
                callback(result);
            },
            error: function(result, status, xhr) {
                callback(result);
            },
            type: 'POST',
            headers: {
                'X-CSRFToken': obj.getCookie('csrftoken')
            }
        });
    };

    return obj;
})();
