import wx
from . import MenuFile, MenuRun


class S:
    NAME_FILE       = "&File"
    NAME_RUN        = "&Action"


def new(parent: wx.Window) -> wx._core.MenuBar:
    bar: wx._core.MenuBar = wx.MenuBar()

    _filemenu = MenuFile.new(parent)
    _runmenu = MenuRun.new(parent)

    bar.Append(_filemenu,   S.NAME_FILE)
    bar.Append(_runmenu,    S.NAME_RUN)

    parent.SetMenuBar(bar)

    return bar
