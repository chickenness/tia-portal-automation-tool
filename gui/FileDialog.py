import wx


class S:
    TITLE_OPEN_CONFIG   = "Open TIA Portal project config"
    WC_OPEN_CONFIG      = "json (*.json)|*.json"


def open_config(frame: wx.Frame) -> str:
    with wx.FileDialog(frame, S.TITLE_OPEN_CONFIG, wildcard=S.WC_OPEN_CONFIG, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
        if fileDialog.ShowModal() == wx.ID_CANCEL:
            return

        return fileDialog.GetPath()
