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
            'pool_name': config.POOL_NAME,
            'login_button': ('Login' if not user else 'Logout {}'.format(user.nickname()))
        }

        template = jinja_environment.get_template('templates/mobile/index.html')
        self.response.out.write(template.render(template_values))

app = webapp2.WSGIApplication([('/', MainPage)],
                              debug=True)
