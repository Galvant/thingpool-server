import config

import webapp2
import jinja2
import os

from google.appengine.api import users

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
                'login_button': 'Logout {}'.format(user.nickname()),
                'loginout_url': users.create_logout_url(self.request.uri)
            })
        else:
            template_values.update({
                'login_button': 'Login',
                'loginout_url': users.create_login_url(self.request.uri)
            })
            

        template = jinja_environment.get_template('templates/mobile/index.html')
        self.response.out.write(template.render(template_values))

app = webapp2.WSGIApplication([('/', MainPage)],
                              debug=True)
