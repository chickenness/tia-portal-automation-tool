from lib.pp import pp
from gui import MenuBar

from pathlib import Path
import wx


class MainWindow(wx.Frame):
    def __init__(self, parent, title) -> None:
        wx.Frame.__init__(self, parent, title=title, size=(600,480))
        self.portal: pp.Portal = None

        self.control = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        self.CreateStatusBar()

        menubar = MenuBar.new(self)

        self.Show(True)


    def OnOpen(self, e):
        with wx.FileDialog(
            self,
            "Open TIA Portal project config",
            wildcard="json (*.json)|*.json",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        ) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            filepath = fileDialog.GetPath()
            try:
                self.portal = pp.parse(filepath)
                self.control.AppendText(f"\n{self.portal.__str__()}")
            except IOError:
                wx.LogError("Cannot open file '%s'." % newfile)

    def OnClose(self, e):
        self.portal = None

    def OnRun(self, e):
        if not isinstance(self.portal, pp.Portal):
            return

        self.portal.run()
        self.control.AppendText(f"\n{self.portal.config}")
        self.control.AppendText(f"\n{self.portal.config.project.devices[0]}")

    def OnExit(self, e):
        self.Close(True)



app = wx.App(False)
frame = MainWindow(None, "TIA Portal Automation Tool")
app.MainLoop()

