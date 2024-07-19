from lib.pp import pp
from gui import MenuBar, FileDialog, Notebook
from pathlib import Path
import wx


class MainWindow(wx.Frame):
    def __init__(self, parent, title) -> None:
        wx.Frame.__init__(self, parent, title=title, size=(800,600))
        self.siemens: pp.Siemens = None
        self.config: pp.objects.Config = None

        self.CreateStatusBar()

        self.menubar = MenuBar.new(self)
        self.notebook = Notebook.new(self)

        self.SetMinSize((600,480))

        self.Show(True)


    def OnOpen(self, e):
        filepath = FileDialog.open_config(self)
        if not filepath:
            return
        self.notebook.tab_project.config_path.write(filepath)
        try:
            data = pp.parse(filepath)
            self.siemens = data['siemens']
            self.config = data['config']
            # self.splitter.tree.populate(self.portal.config)

        except IOError:
            wx.LogError("Cannot open file '%s'." % newfile)

    def OnClose(self, e):
        self.siemens = None
        self.config = None

    def OnRun(self, e):
        if not isinstance(self.siemens, pp.Siemens):
            return

        self.automate()

    def OnExit(self, e):
        self.Close(True)
        self.Destroy()
    
    def automate(self) -> None:
        instance = pp.create_tia_instance(self.siemens, self.config)
        project = pp.create_project(self.siemens, instance, self.config.project.name, self.config.project.directory)
        pp.add_devices(project, self.config.project.devices)
            



if __name__ == '__main__':
    app = wx.App(False)
    frame = MainWindow(None, title="TIA Portal Automation Tool")
    app.MainLoop()

