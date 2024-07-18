import wx


class S:
    LABEL_BROWSE    = "Browse project config"
    SIZE_BROWSE     = (300, -1)

class TextBox(wx.TextCtrl):
    def __init__(self, parent: wx.Window, **kwargs) -> None:
        wx.TextCtrl.__init__(self, parent, **kwargs)

def browse(parent: wx.Window) -> wx.TextCtrl:
    textbox = TextBox(parent, size=S.SIZE_BROWSE)

    return textbox
