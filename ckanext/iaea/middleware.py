class RestrictMiddleware(object):

    def __init__(self, app, app_config):
        self.app=app
    
    def __call__(self, environ, start_response):
        ui_path = environ.get('PATH_INFO')

        if ui_path == "/stats" and not 'repoze.who.identity' in environ:
            
            status = u'404 Not Found'
            location = u'/user/login'
            headers = [(u'Location',location), (u'Content-type', u'text/plain')]
            body='Not authorized to see this page'
            start_response (status, headers)  
            return[body]
        else:
            return self.app(environ, start_response)