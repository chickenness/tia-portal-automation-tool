import wx

from . import Button, TextBox

class S:
    FLAG_SIZER_H        = wx.ALL|wx.EXPAND
    FLAG_SIZER_V        = wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP
    BORDER              = 5


class Panel(wx.Panel):
    def __init__(self, parent: wx.Window, **kwargs) -> None:
        wx.Panel.__init__(self, parent, **kwargs)


def project(parent: wx.Window) -> wx.Panel:
    panel = Panel(parent)

    _vsizer = wx.BoxSizer(wx.VERTICAL)
    _hsizer = wx.BoxSizer(wx.HORIZONTAL)

    panel.config_path: wx.TextCtrl  = TextBox.browse(panel)
    panel.browse: wx.Button         = Button.browse(panel)
    panel.execute: wx.Button        = Button.execute(panel)

    _hsizer.Add(panel.config_path,  proportion=1,           flag=S.FLAG_SIZER_H,
                border=S.BORDER
                )
    _hsizer.Add(panel.browse,       flag=wx.ALL,            border=S.BORDER)
    _hsizer.Add(panel.execute,      flag=wx.ALL,            border=S.BORDER)
    _vsizer.Add(_hsizer,            flag=S.FLAG_SIZER_V,    border=S.BORDER)


    panel.logs: wx.TextCtrl = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
    panel.override_path: wx.CheckBox = wx.CheckBox(panel, label="Override Config Project Path")
    panel.override_path.SetValue(True)

    _vsizer.Add(panel.override_path,  flag=S.FLAG_SIZER_H, border=S.BORDER)
    _vsizer.Add(panel.logs, proportion=1, flag=S.FLAG_SIZER_H, border=S.BORDER)

    panel.SetSizer(_vsizer)

    return panel
