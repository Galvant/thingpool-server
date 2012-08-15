#!/usr/bin/python
# -*- coding: utf-8 -*-
##
# api.py: Definitions of API methods.
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

class newUser(webapp2.RequestHandler):
    def post(self):
        # TODO: Handle new user creation
        
class modifyUser(webapp2.RequestHandler):
    def post(self):
        # TODO: Handle changing user settings
        # If permission = admin or manager, allow permission changes for those below

class queryUserList(webapp2.RequestHandler):
    def post(self):
        # TODO: Return list of users filtered by desired permission level
        # Restricted to admin & manager

class newItem(webapp2.RequestHandler):
    def post(self):
        # TODO: Handle adding a new item to datastore

class modifyItem(webapp2.RequestHandler):
    def post(self):
        # TODO: Handle changing item properties
        # Naturally, this should be restricted to admins or managers
        # Deleting an item should probably be included in here

class queryItemList(webapp2.RequestHandler):
    def post(self):
        # TODO: Handle adding a new item to datastore

class checkoutItem(webapp2.RequestHandler):
    def post(self):
        # TODO: Handle checking out of item.
        # This includes direct item transfer without explicit 'checkin'
        # Also includes clearing outstanding requests if required
        
class checkinItem(webapp2.RequestHandler):
    def post(self):
        # TODO: Handle item checkin process
        
class requestItem(webapp2.RequestHandler):
    def post(self):
        # TODO: Handle item request process
        
class queryCheckoutList(webapp2.RequestHandler):
    def post(self):
        # TODO: Return list of current / historical checkouts a user has performed
        # Admin & manager should be able to do this against other user accounts
        
class queryRequestList(webapp2.RequestHandler):
    def post(self):
        # TODO: Return list of current / historical item requests a user has performed
        # Admin & manager should be able to do this against other user accounts
