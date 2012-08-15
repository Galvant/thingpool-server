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

import dataModels

from google.appengine.api import users

class newUser(webapp2.RequestHandler):
    def post(self):
        # Note, anyone can request an account 
        # TODO: Add check if currently a user before trying to add, and deny those who are banned 
        p = Person(
                    user_account = users.get_current_user(),
                    permissions = 3 # Set to 'requested' status
                    ) 
        p.put()
        
class modifyUser(webapp2.RequestHandler):
    def post(self):
        # TODO: Handle changing user settings
        # If permission = admin or manager, allow permission changes for those below

class queryUserList(webapp2.RequestHandler):
    def post(self):
        # TODO: Return result to user (json?)
        user = users.get_current_user()
        q = Person.all().filter('user_account = ', user)
        if q.get().permissions in [0,1]: # if admin or manager
            q = Person.all().filter('permissions = ', self.request.get('permissions'))

class newItem(webapp2.RequestHandler):
    def post(self):
        # TODO: Generate item ID right here, should not be user defined
        user = users.get_current_user()
        q = Person.all().filter('user_account = ', user)
        if q.get().permissions in [0,1]: # if admin or manager
            item = Item(
                        id_number = self.request.get('id_number'),
                        name = self.request.get('name')
                        )
            item.put()

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
        # TODO: 
        #       - This includes direct item transfer without explicit 'checkin'
        #           - Clear previous checkout transaction (call checkin)
        #           - Deny if same user already has it checked out
        #       - Also includes clearing outstanding requests if required
        user = users.get_current_user()
        q = Person.all().filter('user_account = ', user)
        user = q.get()
        if user.permissions in [0,1,2]: # if admin, manager, or user
            q = Item.all().filter('item_id = ', self.request.get('item_id'))
            
            c = CheckoutTransaction(
                                    item=q.get(),
                                    holder = user
                                    )
            c.put()
        
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
