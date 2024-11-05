from pathlib import Path
import argparse
import wx

from modules import config_schema, portal

class MainWindow(wx.Frame):
    def __init__(self, parent, title) -> None:
        wx.Frame.__init__(self, parent, title=title, size=(800,600))
        # self.config: pp.objects.Config = None
        self.config_path: str = ""

        self.CreateStatusBar()

        menubar = MenuBar.new(self)
        notebook = Notebook.new(self)
        self.tab_conf_textbox = notebook.tab_project.config_path
        self.override_path: wx.CheckBox = notebook.tab_project.override_path
        self.splitter: wx.SplitterWindow = notebook.tab_config

        self.SetMinSize((600,480))

        self.logs = notebook.tab_project.logs
        log.setup(self.logs, 10)

        self.Show(True)



    def OnOpen(self, e):
        self.config_path = FileDialog.open_config(self)
        if not self.config_path:
            return

        self.tab_conf_textbox.write(self.config_path)
        try:
            self.config = pp.parse(self.config_path)
            pp.tia, pp.comp, pp.hwf = pp.import_siemens_module(self.config.dll)

            self.splitter.tree.populate(self.config)

        except IOError:
            wx.LogError("Cannot open file '%s'." % newfile)

    def OnClose(self, e):
        pp.tia = None
        pp.comp = None
        pp.hwf = None
        self.config = None

    def OnRun(self, e):
        pass


    def OnSelectConfigTree(self, e):
        item = e.GetItem()
        value = self.splitter.tree.GetItemData(item)

        if value is not None:
            self.splitter.value.SetValue(str(value))
        else:
            self.splitter.value.SetValue("")


    def OnExit(self, e):
        self.Close(True)
        self.Destroy()
    



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="A simple tool for automating TIA Portal projects.")
    parser.add_argument("-c", "--config",
                        type=Path,
                        help="JSON config file path"
                        )
    parser.add_argument("--dll",
                        type=Path,
                        help="Siemens.Engineering.dll path",
                        default=r"C:/Program Files/Siemens/Automation/Portal V18/PublicAPI/V18/Siemens.Engineering.dll"
                        )
    parser.add_argument("--debug",
                        action="store_true",
                        help="Set log level to DEBUG"
                        )
    args = parser.parse_args()

    json_config = args.config
    dll = args.dll
    debug = args.debug

    if json_config:
        import json
        with open(json_config) as file:
            config = json.load(file)
            validated_config = config_schema.validate_config(config)

        import clr
        from System.IO import DirectoryInfo, FileInfo

        clr.AddReference(dll.as_posix())
        import Siemens.Engineering as SE

        print("TIA Portal Automation Tool")
        print()

        portal.execute(
            SE,
            validated_config,
            {
                "DirectoryInfo": DirectoryInfo,
                "FileInfo": FileInfo,
                "enable_ui": True,
            }
        )
    else:
        app = wx.App(False)
        frame = MainWindow(None, title="TIA Portal Automation Tool")
        app.MainLoop()

