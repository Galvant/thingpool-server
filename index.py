#!/usr/bin/python
# -*- coding: utf-8 -*-
##
# index.py:
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

## THINGPOOL MODULES ##
import api
import config
import mobile_site

## CORE SERVER #################################################################

routes = [
    # Mobile site routes
    webapp2.Route('/',
        handler=mobile_site.MainPage,
        name='mobile_main'),
    
    # API routes
    webapp2.Route('/api/users',
        handler=api.UserListHandler,
        name='api_users_list'
        ),
    webapp2.Route('/api/users/<user_id>',
        handler=api.UserHandler,
        name='api_user'
        ),
    webapp2.Route('/api/items',
        handler=api.ItemListHandler,
        name='api_item_list'
        ),
    webapp2.Route('/api/items/<item_id>',
        handler=api.ItemHandler,
        name='api_item'
        ),
]

app = webapp2.WSGIApplication(
    routes=routes,
    debug=True)
