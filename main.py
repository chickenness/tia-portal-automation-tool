from lib.pp import pp
from gui import MenuBar, FileDialog, Notebook
import wx


class MainWindow(wx.Frame):
    def __init__(self, parent, title) -> None:
        wx.Frame.__init__(self, parent, title=title, size=(800,600))
        self.config: pp.objects.Config = None

        self.CreateStatusBar()

        menubar = MenuBar.new(self)
        notebook = Notebook.new(self)
        self.tab_conf_textbox = notebook.tab_project.config_path

        self.SetMinSize((600,480))

        self.Show(True)


    def OnOpen(self, e):
        filepath = FileDialog.open_config(self)
        if not filepath:
            return

        self.tab_conf_textbox.write(filepath)
        try:
            self.config = pp.parse(filepath)
            pp.tia, pp.comp, pp.hwf = pp.import_siemens_module(self.config.dll)
            # self.splitter.tree.populate(self.portal.config)

        except IOError:
            wx.LogError("Cannot open file '%s'." % newfile)

    def OnClose(self, e):
        pp.tia = None
        pp.comp = None
        pp.hwf = None
        self.config = None

    def OnRun(self, e):
        if pp.tia == None or pp.comp == None or pp.hwf == None:
            return

        pp.execute(self.config)

    def OnExit(self, e):
        self.Close(True)
        self.Destroy()
    

if __name__ == '__main__':
    app = wx.App(False)
    frame = MainWindow(None, title="TIA Portal Automation Tool")
    app.MainLoop()

