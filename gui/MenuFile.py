import wx


class S:
    NAME_OPEN       = "&Open"
    DESC_OPEN       = " Open project configuration."
    NAME_CLOSE      = "&Close"
    DESC_CLOSE      = " Close current configuration."
    NAME_EXIT       = "&Exit"
    DESC_EXIT       = "Terminate this tool. (Does not close TIA Portal)"


def new(frame: wx.Frame) -> wx._core.Menu:
    menu: wx._core.Menu = wx.Menu()

    _open: wx._core.MenuItem   = menu.Append(wx.ID_OPEN, S.NAME_OPEN, S.DESC_OPEN)
    _close: wx._core.MenuItem  = menu.Append(wx.ID_CLOSE, S.NAME_CLOSE, S.DESC_CLOSE)
    menu.AppendSeparator()
    _exit: wx._core.MenuItem   = menu.Append(wx.ID_EXIT, S.NAME_EXIT, S.DESC_EXIT)

    frame.Bind(wx.EVT_MENU, frame.OnOpen, _open)
    frame.Bind(wx.EVT_MENU, frame.OnExit, _exit)
    frame.Bind(wx.EVT_MENU, frame.OnClose, _close)
    
    return menu
