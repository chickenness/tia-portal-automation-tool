import wx


class S:
    LABEL_BROWSE    = "Browse"
    LABEL_EXECUTE   = "Execute"

class Button(wx.Button):
    def __init__(self, parent: wx.Window, **kwargs) -> None:
        wx.Button.__init__(self, parent, **kwargs)
        self.root = wx.GetTopLevelParent(self)

    def bind(self, cmd):
        self.root.Bind(wx.EVT_BUTTON, cmd, self)

def browse(parent: wx.Window) -> wx.Button:
    button = Button(parent, label=S.LABEL_BROWSE)
    button.bind(button.root.OnOpen)

    return button

def execute(parent: wx.Window) -> wx.Button:
    button = Button(parent, label=S.LABEL_EXECUTE)
    button.bind(button.root.OnRun)

    return button
