#!/usr/bin/python
# -*- coding: utf-8 -*-
##
# security.py: Constants and methods for implementing security models.
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

## IMPORTS ##

from functools import wraps
from google.appengine.api import users

import logging

import dataModels

## CONSTANTS ###################################################################

# Note that an /ordering/ is implied here. A Requested user can do anything
# a banned user can do, while an admin can do anything a manager can do.
USER_STATUS_BANNED    = -1
USER_STATUS_UNKNOWN   =  0 # To be used if the permissions level is unknown.
USER_STATUS_REQUESTED =  1
USER_STATUS_USER      =  2
USER_STATUS_KIOSK     =  3 # Able to checkout under other's accounts
USER_STATUS_MANAGER   =  4
USER_STATUS_ADMIN     =  5

USER_STATUS_DESCRIPTIONS = {
    USER_STATUS_BANNED:    'banned',
    USER_STATUS_UNKNOWN:   'none',
    USER_STATUS_REQUESTED: 'requested',
    USER_STATUS_USER:      'user',
    USER_STATUS_KIOSK:     'kiosk',
    USER_STATUS_MANAGER:   'manager',
    USER_STATUS_ADMIN:     'admin'
}

## UTILITY FUNCTIONS ###########################################################

def request_tp_account(user):
    person = dataModels.Person(
        user_account = user,
        permissions = USER_STATUS_REQUESTED
        )
    person.put()

## DECORATORS ##################################################################

def get_current_person():
    user = users.get_current_user()
    return dataModels.Person.all().filter('user_account =', user).get()

def require_permission(perm, reason=None):
    # assert hasattr(Person(), 'can_' + perm)

    # TODO:  The eventual implementation should use reason as an explanation of
    #        a denial if the permission is not present.
    def decorator(method):
        @wraps(method)
        def wrapped_method(self, *args, **kwargs):
            if users.is_current_user_admin():
                # Skip all permissions checking for GAE admins.
                logging.info('Permissions checking on {action} skipped for GAE admin user {acct}.'.format(action=self.request.uri, acct=users.get_current_user()))
                return method(self, *args, **kwargs)
        
            person = get_current_person()
            
            if person is not None:
            
                if getattr(person, 'can_' + perm):
                    return method(self, *args, **kwargs)
                else:
                    logging.info('Action {action} denied to {acct} due to not having the permission {perm}.'.format(action=self.request.uri, acct=person.user_account, perm=perm))
                    self.error(403) # TODO: explain to user.                    
            else:
                logging.info('Action {action} denied to {acct} due to not having a ThingPool account.'.format(action=self.request.uri, acct=person.user_account))
                self.error(403) # TODO: explain to user.
    
        return wrapped_method
        
    return decorator

def require_gae_login(mode='redirect'):
    """
    Decorates a RequestHandler method such that it requires a GAE login
    (though not a ThingPool login to match), and if this is not provided,
    either redirects the request or responds with an HTTP error.
    
    :param str redirect: Either "redirect" if the user is to be redirected to
        a login page, of "deny" if the user is to be presented with a 403 error.        
    """
    
    def redirect_decorator(method):
        @wraps(method)
        def wrapped_method(self, *args, **kwargs):
            user = users.get_current_user()
            if not user:
                self.redirect(user.create_login_url(self.request.uri))
                return
                
            # Pass along to the wrapped method.
            method(self, *args, **kwargs)
            
        return wrapped_method
            
    def deny_decorator(method):
        @wraps(method)
        def wrapped_method(self, *args, **kwargs):
            user = users.get_current_user()
            if not user:
                # TODO: write out a JSON API denial.
                self.error(403)
                return
                
            method(self, *args, **kwargs)
            
        return wrapped_method
            
    decorators = {
        'redirect': redirect_decorator,
        'deny': deny_decorator
    }
    
    return decorators[mode]

