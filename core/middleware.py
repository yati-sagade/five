

class FiveMiddleware(object):
    '''
    Middleware for debugging and other stuff

    '''
    def process_request(self, request):
        if request.method == 'POST':
            import pdb
            pdb.set_trace()
        return None
