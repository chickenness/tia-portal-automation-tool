import wx


def log(parent: wx.Window) -> wx.Panel:
    panel = wx.Panel(parent)

    _logs = wx.TextCtrl(
        panel,
        style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_NO_VSCROLL,
    )

    _sizer = wx.BoxSizer(wx.HORIZONTAL)
    _sizer.Add(_logs, proportion=3, flag=wx.EXPAND | wx.ALL, border=10)
    # _sizer.AddStretchSpacer(prop=7)

    panel.SetSizer(_sizer)

    return panel

def project(parent: wx.Window) -> wx.Panel:
    panel = wx.Panel(parent)

    return panel

def settings(parent: wx.Window) -> wx.Panel:
    panel = wx.Panel(parent)

    return panel
