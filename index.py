import webapp2

from google.appengine.api import users

class MainPage(webapp2.RequestHandler):
	def get(self):
		
		user = users.get_current_user()
		
		self.response.headers['Content-Type'] = 'text/plain'
		self.response.out.write('Hello World, this is Thingpool!\n')
		
		if user:
			self.response.out.write( 'Your name is ' + user.nickname() )
		else:
			self.redirect( users.create_login_url(self.request.uri) )

app = webapp2.WSGIApplication([('/', MainPage)],
                              debug=True)
