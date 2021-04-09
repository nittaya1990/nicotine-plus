# COPYRIGHT (C) 2020-2021 Nicotine+ Team
# COPYRIGHT (C) 2016-2018 Mutnick <mutnick@techie.com>
# COPYRIGHT (C) 2016-2017 Michael Labouebe <gfarmerfr@free.fr>
# COPYRIGHT (C) 2009-2011 Quinox <quinox@users.sf.net>
# COPYRIGHT (C) 2009 Hedonist <ak@sensi.org>
# COPYRIGHT (C) 2006-2008 Daelstorm <daelstorm@gmail.com>
# COPYRIGHT (C) 2003-2004 Hyriand <hyriand@thegraveyard.org>
#
# GNU GENERAL PUBLIC LICENSE
#    Version 3, 29 June 2007
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os

from pynicotine.gtkgui.dialogs import option_dialog
from pynicotine.gtkgui.transferlist import TransferList
from pynicotine.gtkgui.utils import open_file_path
from pynicotine.gtkgui.utils import PopupMenu


class Uploads(TransferList):

    def __init__(self, frame, tab_label):

        TransferList.__init__(self, frame, type='upload')
        self.tab_label = tab_label

        self.popup_menu_users = PopupMenu(frame)

        self.popup_menu_clear = PopupMenu(frame)
        self.popup_menu_clear.setup(
            ("#" + _("Clear Finished / Failed"), self.on_clear_finished_failed),
            ("#" + _("Clear Finished / Aborted"), self.on_clear_finished_aborted),
            ("#" + _("Clear Finished"), self.on_clear_finished),
            ("#" + _("Clear Aborted"), self.on_clear_aborted),
            ("#" + _("Clear Failed"), self.on_clear_failed),
            ("#" + _("Clear Queued"), self.on_clear_queued)
        )

        self.popup_menu = PopupMenu(frame)
        self.popup_menu.setup(
            ("#" + "selected_files", None),
            ("", None),
            ("#" + _("Send to _Player"), self.on_play_files),
            ("#" + _("_Open Folder"), self.on_open_directory),
            ("", None),
            ("#" + _("Copy _File Path"), self.on_copy_file_path),
            ("#" + _("Copy _URL"), self.on_copy_url),
            ("#" + _("Copy Folder URL"), self.on_copy_dir_url),
            ("", None),
            ("#" + _("_Search"), self.on_file_search),
            (">" + _("User(s)"), self.popup_menu_users),
            ("", None),
            ("#" + _("_Retry"), self.on_retry_transfer),
            ("#" + _("Abor_t"), self.on_abort_transfer),
            ("#" + _("_Clear"), self.on_clear_transfer),
            ("", None),
            (">" + _("Clear Groups"), self.popup_menu_clear)
        )

    def on_try_clear_queued(self, *args):
        option_dialog(
            parent=self.frame.MainWindow,
            title=_('Clear Queued Uploads'),
            message=_('Are you sure you wish to clear all queued uploads?'),
            callback=self.on_clear_response
        )

    def on_open_directory(self, *args):

        downloaddir = self.frame.np.config.sections["transfers"]["downloaddir"]
        incompletedir = self.frame.np.config.sections["transfers"]["incompletedir"]

        if incompletedir == "":
            incompletedir = downloaddir

        transfer = next(iter(self.selected_transfers))

        if os.path.exists(transfer.path):
            final_path = transfer.path
        else:
            final_path = incompletedir

        # Finally, try to open the directory we got...
        command = self.frame.np.config.sections["ui"]["filemanager"]
        open_file_path(final_path, command)

    def on_play_files(self, *args):

        for fn in self.selected_transfers:
            playfile = fn.realfilename

            if os.path.exists(playfile):
                command = self.frame.np.config.sections["players"]["default"]
                open_file_path(playfile, command)

    def on_popup_menu(self, *args):

        self.select_transfers()
        num_selected_transfers = len(self.selected_transfers)

        actions = self.popup_menu.get_actions()
        users = len(self.selected_users) > 0
        files = num_selected_transfers > 0

        actions[_("User(s)")].set_enabled(users)  # Users Menu
        self.populate_popup_menu_users()

        if files:
            act = True
        else:
            # Disable options
            # Send to player, File manager, Copy File Path, Copy URL, Copy Folder URL, Search filename
            act = False

        for i in (_("Send to _Player"), _("_Open Folder"), _("Copy _File Path"),
                  _("Copy _URL"), _("Copy Folder URL"), _("_Search")):
            actions[i].set_enabled(act)

        if users and files:
            act = True
        else:
            # Disable options
            # Retry, Abort, Clear
            act = False

        for i in (_("_Retry"), _("Abor_t"), _("_Clear")):
            actions[i].set_enabled(act)

        self.popup_menu.set_num_selected_files(num_selected_transfers)

        self.popup_menu.popup()
        return True

    def double_click(self, event):

        self.select_transfers()
        dc = self.frame.np.config.sections["transfers"]["upload_doubleclick"]

        if dc == 1:  # Send to player
            self.on_play_files()
        elif dc == 2:  # File manager
            self.on_open_directory()
        elif dc == 3:  # Search
            self.on_file_search()
        elif dc == 4:  # Abort
            self.on_abort_transfer()
        elif dc == 5:  # Clear
            self.on_clear_transfer()

    def clear_by_user(self, user):

        for i in self.list[:]:
            if i.user == user:
                self.remove_specific(i)

    def on_abort_user(self, *args):

        self.select_transfers()

        for user in self.selected_users:
            for i in self.list:
                if i.user == user:
                    self.selected_transfers.add(i)

        self.on_abort_transfer()

    def on_clear_aborted(self, *args):
        self.clear_transfers(["Aborted", "Cancelled", "User logged off"])

    def on_clear_failed(self, *args):
        self.clear_transfers(["Cannot connect", "Local file error", "Remote file error"])

    def on_clear_finished_aborted(self, *args):
        self.clear_transfers(["Aborted", "Cancelled", "User logged off", "Finished"])

    def on_clear_finished_failed(self, *args):
        self.clear_transfers(["Aborted", "Cancelled", "User logged off", "Finished", "Cannot connect", "Local file error", "Remote file error"])
