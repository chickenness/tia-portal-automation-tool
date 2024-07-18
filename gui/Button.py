import wx


class S:
    LABEL_BROWSE    = "Browse"
    LABEL_EXECUTE   = "Execute"

class Button(wx.Button):
    def __init__(self, parent: wx.Window, **kwargs) -> None:
        wx.Button.__init__(self, parent, **kwargs)

def browse(parent: wx.Window) -> wx.Button:
    button = Button(parent, label=S.LABEL_BROWSE)
    _root = wx.GetTopLevelParent(button)
    _root.Bind(wx.EVT_BUTTON, _root.OnOpen, button)

    return button

def execute(parent: wx.Window) -> wx.Button:
    button = Button(parent, label=S.LABEL_EXECUTE)

    return button
