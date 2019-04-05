# -*- coding: utf-8 -*-
#
#   package_info.py — package_info table model
#
#   This file is part of debexpo -
#   https://salsa.debian.org/mentors.debian.net-team/debexpo
#
#   Copyright © 2008 Jonny Lamb <jonny@debian.org>
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
Holds package_info table model.
"""

__author__ = 'Jonny Lamb'
__copyright__ = 'Copyright © 2008 Jonny Lamb'
__license__ = 'MIT'

import json
import os

from mako.lookup import TemplateLookup
from mako.exceptions import TopLevelLookupException

from pylons import config

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.orm import backref

import debexpo.lib

from debexpo.model import meta, OrmObject
from debexpo.model.package_versions import PackageVersion

# templates are in [...]/templates/plugins
PLUGINS_TEMPLATE_DIRS = [os.path.join(path, "plugins")
                         for path in config["pylons.paths"]["templates"]]

t_package_info = sa.Table(
    'package_info', meta.metadata,
    sa.Column('id', sa.types.Integer, primary_key=True),
    sa.Column('package_version_id', sa.types.Integer,
              sa.ForeignKey('package_versions.id')),
    sa.Column('from_plugin', sa.types.String(200), nullable=False),
    sa.Column('outcome', sa.types.String(200), nullable=False),
    sa.Column('data', sa.types.Text, nullable=True),
    sa.Column('severity', sa.types.Integer, nullable=False),
    )


class PackageInfo(OrmObject):
    foreign = ['package_version']

    @property
    def rich_data(self):
        try:
            return json.loads(self.data)
        except ValueError:
            return self.data

    @rich_data.setter
    def rich_data(self, value):
        self.data = json.dumps(value)

    def render(self, render_format):
        """Render the plugin data to the given format"""

        # Files to try out for plugin data rendering
        try_files = [
            "%s/%s.mako" % (self.from_plugin, render_format),
            "%s/text.mako" % (self.from_plugin),
            "default/%s.mako" % render_format,
            "default/text.mako",
            ]

        lookup = TemplateLookup(
            directories=PLUGINS_TEMPLATE_DIRS,
            input_encoding='utf-8',
            output_encoding='utf-8',
            default_filters=['escape'],
            imports=['from webhelpers.html import escape',
                     'from debexpo.lib.filters import semitrusted']
            )

        for basefile in try_files:
            try:
                template = lookup.get_template(basefile)
            except TopLevelLookupException:
                continue
            else:
                break
        else:
            # No template file found, something weird happened
            return "%s (!! no template found)" % self.data  # pragma: no cover

        return template.render_unicode(o=self, h=debexpo.lib.helpers)


orm.mapper(PackageInfo, t_package_info, properties={
    'package_version': orm.relation(
        PackageVersion,
        backref=backref('package_info', cascade='all, delete-orphan')),
})
