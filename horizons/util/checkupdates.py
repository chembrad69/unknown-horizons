# ###################################################
# Copyright (C) 2008-2013 The Unknown Horizons Team
# team@unknown-horizons.org
# This file is part of Unknown Horizons.
#
# Unknown Horizons is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the
# Free Software Foundation, Inc.,
# 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# ###################################################

import webbrowser
import urllib
import urllib2

from fife.extensions.pychan.widgets import Button

from horizons.constants import NETWORK, VERSION
from horizons.gui.windows import Popup


class UpdateInfo(object):
	INVALID, READY, UNINITIALIZED = range(3)
	def __init__(self):
		self.status = UpdateInfo.UNINITIALIZED
		self.version = None
		self.link = None

TIMEOUT = 5.0 # we should be done before the user can start a game
def check_for_updates(info):
	"""Check if there's a new version.
	@return update file contents or None"""
	# make sure to always set info.status, but only when we're done
	if VERSION.IS_DEV_VERSION: # no updates for git version
		info.status = UpdateInfo.INVALID
		return

	# retrieve current version w.r.t. the local version.
	# this way, possible configurations of different most recent versions should be handleable in the future.
	data = urllib.urlencode( {"my_version" : VERSION.RELEASE_VERSION} )
	url = NETWORK.UPDATE_FILE_URL
	try:
		u = urllib2.urlopen( url + "?" + data, timeout=TIMEOUT )
	except urllib2.URLError as e:
		# Silently ignore the failed update, printing stuff might crash the game
		# if no console is available
		info.status = UpdateInfo.INVALID
		return

	version = u.readline()
	link = u.readline()
	u.close()

	version = version[:-1] # remove newlines
	link = link[:-1] # remove newlines

	if version != VERSION.RELEASE_VERSION:
		# there is a new version
		info.version = version
		info.link = link
		info.status = UpdateInfo.READY
	else:
		info.status = UpdateInfo.INVALID


class VersionHint(Popup):

	def __init__(self, windows, info):
		self.info = info

		title = _("New version of Unknown Horizons")
		text = _("There is a more recent release of Unknown Horizons ({new_version}) "
				 "than the one you are currently using ({old_version}).").format(
				new_version=info.version,
				old_version=VERSION.RELEASE_VERSION)

		super(VersionHint, self).__init__(windows, title, text)

	def prepare(self, **kwargs):
		super(VersionHint, self).prepare(**kwargs)

		dl_btn = Button(name="dl", text=_("Click to download"))
		dl_btn.position = (48, 138) # i've tried, this button cannot be placed in a sane way
		def do_dl():
			webbrowser.open(self.info.link)
			dl_btn.text = _("A page has been opened in your browser.")
			self._gui.adaptLayout()
		dl_btn.capture(do_dl)

		self._gui.addChild(dl_btn)


def show_new_version_hint(gui, info):
	"""
	@param gui: main gui (Gui)
	@param info: UpdateInfo instance
	"""
	window = VersionHint(gui.windows, info)
	gui.windows.show(window)
