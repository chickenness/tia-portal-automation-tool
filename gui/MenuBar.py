import wx
from . import MenuFile, MenuRun


class S:
    NAME_FILE       = "&File"
    NAME_RUN        = "&Run"


def new(frame: wx.Frame) -> wx._core.MenuBar:
    bar: wx._core.MenuBar = wx.MenuBar()

    _filemenu = MenuFile.new(frame)
    _runmenu = MenuRun.new(frame)

    bar.Append(_filemenu, S.NAME_FILE)
    bar.Append(_runmenu, S.NAME_RUN)

    frame.SetMenuBar(bar)

    return bar
