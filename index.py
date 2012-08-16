import config

import webapp2
import jinja2
import os

from google.appengine.api import users

import api

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class MainPage(webapp2.RequestHandler):
    def get(self):
        	
        user = users.get_current_user()
        
        self.response.headers['Content-Type'] = 'text/html'	
        
        template_values = {
            'pool_name': config.POOL_NAME
        }
        
        # Avoid having to put an if operator in every single value by updating
        # the dictionary differently if we're logged in or not.
        if user:
            template_values.update({
                'login_button': 'Logout',
                'loginout_url': users.create_logout_url(self.request.uri),
                'checked_out_things': 12, # FIXME: this is for mockup purposes ONLY.
                'username': user.nickname()
            })
        else:
            template_values.update({
                'login_button': 'Login',
                'loginout_url': users.create_login_url(self.request.uri),
                'checked_out_things': 0,
                'username' : 'Not logged in'
            })
            

        template = jinja_environment.get_template('templates/mobile/index.html')
        self.response.out.write(template.render(template_values))

routes = [
    # Mobile site routes
    ('/', MainPage),
    
    # API routes
    ('/api/users', api.UsersHandler),
    ('/api/users/<user_id>', api.UserHandler), # TODO: Add user_id argument to UserHandler.
    # ('/api/items', ),
    # ('/api/items/<item_id>', ),
]

app = webapp2.WSGIApplication(
    routes=routes,
    debug=True)
