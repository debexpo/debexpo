# -*- coding: utf-8 -*-
#
#   routing.py — Routes configuration
#
#   This file is part of debexpo - http://debexpo.workaround.org
#
#   Copyright © 2008 Jonny Lamb <jonny@debian.org>
#   Copyright © 2010 Jan Dittberner <jandd@debian.org>
#
#   Permission is hereby granted, free of charge, to any person
#   obtaining a copy of this software and associated documentation
#   files (the "Software"), to deal in the Software without
#   restriction, including without limitation the rights to use,
#   copy, modify, merge, publish, distribute, sublicense, and/or sell
#   copies of the Software, and to permit persons to whom the
#   Software is furnished to do so, subject to the following
#   conditions:
#
#   The above copyright notice and this permission notice shall be
#   included in all copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#   EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
#   OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#   NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#   HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
#   WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#   FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#   OTHER DEALINGS IN THE SOFTWARE.

"""
Routes configuration

The more specific and detailed routes should be defined first so they
may take precedent over the more generic routes. For more information
refer to the routes manual at http://routes.groovie.org/docs/
"""
__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb, Copyright © 2010 Jan Dittberner'
__license__ = 'MIT'

from routes import Mapper

def make_map(config):
    """
    Creates, configures and returns the routes Mapper.
    """
    map = Mapper(directory=config['pylons.paths']['controllers'],
                 always_scan=config['debug'])
    map.minimization = False

    # The ErrorController route (handles 404/500 error pages); it should
    # likely stay at the top, ensuring it can always be resolved
    map.connect('error/{action}', controller='error')
    map.connect('error/{action}/{id}', controller='error')

    # CUSTOM ROUTES HERE

    if config['debexpo.handle_debian'].lower() == 'true':
        map.connect('/debian/*filename', controller='debian', action='index')

    map.connect('index', '/', controller='index', action='index')
    map.connect('contact', '/contact', controller='index', action='contact')
    map.connect('intro-maintainers', '/intro-maintainers',
                controller='index', action='intro_maintainers')
    map.connect('sponsors', '/sponsors', controller='sponsor', action='index')
    map.connect('sponsor-developer', '/sponsors/profile/{id}', controller='sponsor', action='developer')
    map.connect('sponsor_tag_save', '/sponsors/save', controller='sponsor', action='save')
    map.connect('sponsor_tag_clear', '/sponsors/clear', controller='sponsor', action='clear')
    map.connect('intro-reviewers', '/intro-reviewers', controller='index', action='intro_reviewers')
    map.connect('my', '/my', controller='my', action='index')
    map.connect('login', '/login', controller='login', action='index')
    map.connect('logout', '/logout', controller='login', action='logout')
    map.connect('news', '/news', controller='index', action='news')
    map.connect('/package', controller='package', action='index')
    map.connect('package', '/package/{packagename}', controller='package', action='index')
    map.connect('comment', '/package/{packagename}/comment', controller='package', action='comment')
    map.connect('sponsor', '/package/{packagename}/needs_sponsor/{key}', controller='package', action='sponsor')
    map.connect('subscribe', '/package/{packagename}/subscribe', controller='package', action='subscribe')
    map.connect('delete', '/package/{packagename}/delete/{key}', controller='package', action='delete')
    map.connect('rfs', '/package/rfs/{packagename}', controller='package', action='rfs')
    map.connect('packages', '/packages/{action}', controller='packages', action='index')
    map.connect('all-packages', '/packages', controller='packages', action='index')
    map.connect('packages-uploader', '/packages/uploader/{id}', controller='packages', action='uploader')
    #map.connect('/packages/{action}/{id}', controller='packages', action='index', id=None)
    #map.connect('packages_filter_feed', '/packages/{filter}/{id}/feed', controller='packages', action='feed')
    #map.connect('packages_feed', '/packages/feed', controller='packages', action='feed')
    map.connect('qa', '/qa', controller='index', action='qa')
    #map.connect('register', '/register/{action}/{id}', controller='register', action='index', id=None)
    map.connect('/upload/{email}/{password}/{filename}', controller='upload',
                action='index')
    map.connect('ppa', '/ppa/{email}', controller='ppa', action='index')
    #map.connect('/ppa/{email}/*filename', controller='ppa', action='file')
    map.connect('/soap.wsdl', controller='soap')

    map.connect('/{controller}/{action}')
    map.connect('/{controller}/{action}/{id}')
    #map.connect('/*url', controller='template', action='view')

    return map
