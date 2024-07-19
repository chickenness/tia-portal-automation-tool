import wx

from . import Tree

class Splitter(wx.SplitterWindow):
    def __init__(self, parent: wx.Window) -> None:
        wx.SplitterWindow.__init__(self, parent, style=wx.SP_LIVE_UPDATE)


def new(parent: wx.Window) -> wx.SplitterWindow:
    splitter: wx.SplitterWindow = Splitter(parent)

    _sty = wx.BORDER_SUNKEN

    splitter.p1 = wx.Window(splitter, style=_sty)
    splitter.p2 = wx.Window(splitter, style=_sty)

    splitter.tree = Tree.new(splitter.p1)

    _p1sizer: wx.BoxSizer = wx.BoxSizer(wx.VERTICAL)
    _p1sizer.Add(splitter.tree, proportion=1, flag=wx.EXPAND|wx.ALL, border=1)
    splitter.p1.SetSizer(_p1sizer)

    splitter.SetMinimumPaneSize(100)
    splitter.SplitVertically(splitter.p1, splitter.p2, 250)
    splitter.SetSashPosition(0)

    return splitter