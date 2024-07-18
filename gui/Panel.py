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

def tree_overview(parent: wx.Window) -> wx.Panel:
    panel: wx.Panel = wx.Panel(parent, style=wx.WANTS_CHARS|wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN)

    _id: wx.WindowIDRef = wx.NewIdRef()
    _tree: wx.TreeCtrl = wx.TreeCtrl(panel,
                                     _id,
                                     wx.DefaultPosition,
                                     wx.DefaultSize,
                                     )
    _root = _tree.AddRoot("TIA Portal")
    _sizer: wx.BoxSizer = wx.BoxSizer(wx.VERTICAL)
    _sizer.Add(_tree, proportion=1, flag=wx.EXPAND|wx.ALL, border=1)

    _sizer.AddStretchSpacer(prop=7)
    panel.SetSizer(_sizer)

    for x in range(15):
        child = _tree.AppendItem(_root, "Item %d" % x)
        _tree.SetItemData(child, None)
        for x in range(5):
            child2 = _tree.AppendItem(child, "Item %d" % x)
            _tree.SetItemData(child2, None)

    _tree.Expand(_root)
    return panel
