# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals
from copy import copy
from traceback import print_exc

from pyload.Api import ProgressInfo, ProgressType
from .basethread import BaseThread


class AddonThread(BaseThread):
    """thread for addons"""

    def __init__(self, m, function, args, kwargs):
        """Constructor"""
        BaseThread.__init__(self, m)

        self.f = function
        self.args = args
        self.kwargs = kwargs

        self.active = []
        self.progress = 0

        m.addThread(self)

        self.start()

    def getActiveFiles(self):
        return self.active

    # TODO: multiple progresses
    def setProgress(self, progress, pyfile=None):
        """  Sets progress for the thread in percent"""
        self.progress = progress

    def getProgress(self):
        """ Progress of the thread  """
        if self.active:
            active = self.active[0]
            return ProgressInfo(active.pluginname, active.name, active.getStatusName(), 0,
                                self.progress, 100, self.owner, ProgressType.Addon)

    def addActive(self, pyfile):
        """ Adds a pyfile to active list and thus will be displayed on overview"""
        if pyfile not in self.active:
            self.active.append(pyfile)

    def finishFile(self, pyfile):
        if pyfile in self.active:
            self.active.remove(pyfile)

        pyfile.finishIfDone()

    def run(self): #TODO: approach via func_code
        try:
            try:
                self.kwargs["thread"] = self
                self.f(*self.args, **self.kwargs)
            except TypeError as e:
                #dirty method to filter out exceptions
                if "unexpected keyword argument 'thread'" not in e.args[0]:
                    raise

                del self.kwargs["thread"]
                self.f(*self.args, **self.kwargs)
        except Exception as e:
            if hasattr(self.f, "im_self"):
                addon = self.f.__self__
                addon.logError(_("An Error occurred"), e)
                if self.m.pyload.debug:
                    print_exc()
                    self.writeDebugReport(addon.__name__, plugin=addon)

        finally:
            local = copy(self.active)
            for x in local:
                self.finishFile(x)

            self.finished()
