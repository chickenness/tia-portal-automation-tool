import wx


class S:
    NAME_OPEN       = "&Open"
    DESC_OPEN       = " Open project configuration."
    NAME_CLOSE      = "&Close"
    DESC_CLOSE      = " Close current configuration."
    NAME_EXIT       = "&Exit"
    DESC_EXIT       = "Terminate this tool. (Does not close TIA Portal)"


def new(parent: wx.Window) -> wx._core.Menu:
    menu: wx._core.Menu = wx.Menu()

    _open: wx._core.MenuItem   = menu.Append(wx.ID_OPEN,    S.NAME_OPEN,    S.DESC_OPEN)
    _close: wx._core.MenuItem  = menu.Append(wx.ID_CLOSE,   S.NAME_CLOSE,   S.DESC_CLOSE)
    menu.AppendSeparator()
    _exit: wx._core.MenuItem   = menu.Append(wx.ID_EXIT,    S.NAME_EXIT,    S.DESC_EXIT)

    parent.Bind(wx.EVT_MENU, parent.OnOpen,     _open)
    parent.Bind(wx.EVT_MENU, parent.OnExit,     _exit)
    parent.Bind(wx.EVT_MENU, parent.OnClose,    _close)
    
    return menu
