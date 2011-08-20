# -*- coding: utf-8 -*-
#
#   importcomments.py — Import RFS comments from debian-mentors
#
#   This file is part of debexpo - http://debexpo.workaround.org
#
#   Copyright © 2011 Arno Töll <debian@toell.net>
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
Import RFS comments from debian-mentors
"""
__author__ = 'Arno Töll'
__copyright__ = 'Copyright © 2011 Arno Töll'
__license__ = 'MIT'

from debexpo.cronjobs import BaseCronjob

from debexpo.model.packages import Package
from debexpo.model import meta
from debian import deb822

import imaplib
import email.parser

class ImportComments(BaseCronjob):
	def _check(self, msg, err, data = None):
		if err != 'OK':
			if (data):
				self.log.error("%s failed: %s" % (msg, data))
			else:
				self.log.error("%s failed: %s" % (msg))

	def _process_changes(self, mail):
		if mail.is_multipart():
			self.log.debug("Changes message is multipart?!")
			return
		changes = mail.get_payload(decode=True)
		try:
			changes = deb822.Changes(changes)
		except:
			self.log.error('Could not open changes file; skipping mail "%s"' % (mail['subject']))
			return

		if not 'Source' in changes:
			self.log.debug('Changes file "%s" seems incomplete' % (mail['subject']))
			return
		package = meta.session.query(Package).filter_by(name=changes['Source']).first()
		if package != None:
			#XXX: Finish me
			pass
		else:
			self.log.debug("Package %s was not uploaded to Expo before - ignoring it" % (changes['Source']))

	def _process_mentors(self, mail):
		pass

	def setup(self):
		self.established = False
		self.server = 'mx.freenet.de'
		self.user = 'debexpo-importer'
		self.passwod = 'ZHz66Sh0Ow9sU'

		self.imap = imaplib.IMAP4(self.server)
		(err, data) = self.imap.login(self.user, self.passwod)
		self._check("IMAP login", err, data)
		if err == 'OK':
			self.established = True

		(err, data) = self.imap.select("INBOX", readonly=True)
		self._check("IMAP select", err, data)

	def teardown(self):
		self.imap.close()
		self.imap.logout()


	def deploy(self):
		print("Running ImportUpload")
		(err, messages) = self.imap.search(None, '(UNSEEN)')
		self._check("IMAP search messages", err)

		for msg_id in messages[0].split(" "):
			#(err, msginfo) = self.imap.fetch(msg_id, '(BODY[HEADER.FIELDS (SUBJECT FROM LIST-ID)])')
			(err, msginfo) = self.imap.fetch(msg_id, 'RFC822')
			self._check("IMAP fetch message", err)
			if (err != 'OK'):
				continue
			ep = email.parser.Parser().parsestr(msginfo[0][1])
			if ep["list-id"] in ('<debian-devel-changes.lists.debian.org>',
					'<debian-changes.lists.debian.org>',
					'<debian-backports-changes.lists.debian.org>'):
				self._process_changes(ep)
			elif ep["list-id"] == '<debian-mentors.lists.debian.org>':
				self._process_mentors(ep)
			else:
				self.log.debug("Unrecognized message in mailbox: '%s'" % ep["subject"])

cronjob = ImportComments
schedule = 1
