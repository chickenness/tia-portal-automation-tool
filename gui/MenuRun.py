import wx


class S:
    NAME_RUN        = "&Run"
    DESC_RUN        = " Run project."


def new(frame: wx.Frame) -> wx._core.Menu:
    menu: wx._core.Menu = wx.Menu()

    _run: wx._core.MenuItem     = menu.Append(wx.NewIdRef(), S.NAME_RUN, S.DESC_RUN)

    frame.Bind(wx.EVT_MENU, frame.OnRun, _run)

    return menu
