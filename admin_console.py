#!/usr/bin/python
# -*- coding: utf-8 -*-
##
# admin_console.py: Implements an administrator console for the ThingPool
#     server.
##
# © 2012 Steven Casagrande (scasagrande@galvant.ca) and
#     Christopher E. Granade (cgranade@cgranade.com).
# This file is a part of the ThingPool Server project.
# Licensed under the AGPL version 3.
##
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
##

## IMPORTS #####################################################################

## GAE API ##
from google.appengine.api import users

## WEB FRAMEWORK
import webapp2
import jinja2

## PYTHON STANDARD LIBRARY ##
import os
import logging

## THINGPOOL MODULES ##
import api
import config
import index
import dataModels
import security

## CORE SERVER #################################################################

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))      
    
base_template_values = {
    'pool_name': config.POOL_NAME,
    'uri_for': webapp2.uri_for,
    'message': None
}
    
class MainPage(webapp2.RequestHandler):

    def _template_values(self):
        template_values = dict(base_template_values)
        
        # List users with USER_STATUS_REQUESTED permissions
        it = dataModels.Person.all().filter('permissions =', security.USER_STATUS_REQUESTED).run()
        pending_requests = list(it)
        template_values['pending_requests'] = pending_requests
        
        # List all useres
        it = dataModels.Person.all()
        all_users = list(it)
        template_values['all_users'] = all_users
        
        return template_values

    @security.require_permission('access_admin')
    @security.require_gae_login('redirect')
    def post(self):
        template_values = self._template_values()
        
        # What action did we get?
        action = self.request.get('action')
        if action == 'handle_account_request':
            # FIXME: must check here the can_resolve_acct_request permission
            user_id = int(self.request.get('user_id'))
            resolution = self.request.get('request_resolution')
            
            requesting_user = dataModels.Person.get_by_id(user_id)
            requesting_user.permissions = (
                security.USER_STATUS_USER if resolution == 'approve' else security.USER_STATUS_BANNED
            )
            requesting_user.put()
            
            template_values['message'] = "Account request resolved."
        else:
            logging.error('Action {} not recognized by admin console.'.format(action))
        
    
        self.response.headers['Content-Type'] = 'text/html'	
        template = jinja_environment.get_template('templates/admin/index.html')
        self.response.out.write(template.render(template_values))
        

    @security.require_permission('access_admin')
    @security.require_gae_login('redirect')
    def get(self):        	    
        self.response.headers['Content-Type'] = 'text/html'	
        template = jinja_environment.get_template('templates/admin/index.html')
        self.response.out.write(template.render(self._template_values()))
        
