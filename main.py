from pathlib import Path
import argparse
import json
import wx

from modules import config_schema, portal, logger

class MainWindow(wx.Frame):
    def __init__(self, parent, title) -> None:
        wx.Frame.__init__(self, parent, title=title, size=(800,600))
        self.config: dict = {}
        self.dll: str = ""

        self.CreateStatusBar()

        # Menubars and menu items
        menubar: wx.MenuBar = wx.MenuBar()
        _filemenu = wx.Menu()
        _open = _filemenu.Append(wx.ID_OPEN, "&Open", " Open project configuration.")
        _close = _filemenu.Append(wx.ID_CLOSE, "&Close", " Close current configuration.")
        _filemenu.AppendSeparator()
        _exit = _filemenu.Append(wx.ID_EXIT, "&Exit", "Terminate this tool. (Does not close TIA Portal)")
        _runmenu = wx.Menu()
        _run = _runmenu.Append(wx.NewIdRef(), "&Run", " Run project.")
        self.Bind(wx.EVT_MENU, self.OnOpen, _open)
        self.Bind(wx.EVT_MENU, self.OnExit, _exit)
        self.Bind(wx.EVT_MENU, self.OnClose, _close)
        self.Bind(wx.EVT_MENU, self.OnRun, _run)
        menubar.Append(_filemenu, "&File")
        menubar.Append(_runmenu, "&Action")
        self.SetMenuBar(menubar)


        # notebook
        notebook: wx.Notebook = wx.Notebook(self)
        _tab_project = wx.Panel(notebook)
        _vsizer = wx.BoxSizer(wx.VERTICAL)
        _hsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.textctrl_config = wx.TextCtrl(_tab_project, size=(300, -1))
        _browse: wx.Button = wx.Button(_tab_project, label="Browse")
        _select_dll: wx.Button = wx.Button(_tab_project, label="Select DLL")
        _execute: wx.Button = wx.Button(_tab_project, label="Execute")
        _hsizer.Add(self.textctrl_config, proportion=1, flag=wx.ALL|wx.EXPAND, border=5)
        _hsizer.Add(_browse, flag=wx.ALL, border=5)
        _hsizer.Add(_select_dll, flag=wx.ALL, border=5)
        _hsizer.Add(_execute, flag=wx.ALL, border=5)
        _vsizer.Add(_hsizer, flag= wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=5)
        self.logs: wx.TextCtrl = wx.TextCtrl(_tab_project, style=wx.TE_MULTILINE)
        # _override_path: wx.CheckBox = wx.CheckBox(_tab_project, label="Override Config Project Path")
        # _override_path.SetValue(True)
        # _vsizer.Add(_override_path, flag=wx.ALL|wx.EXPAND, border=5)
        _vsizer.Add(self.logs, proportion=1, flag=wx.ALL|wx.EXPAND, border=5)
        _tab_project.SetSizer(_vsizer)
        self.Bind(wx.EVT_BUTTON, self.OnOpen, _browse)
        self.Bind(wx.EVT_BUTTON, self.OnRun, _execute)
        self.Bind(wx.EVT_BUTTON, self.OnSelectDLL, _select_dll)
        _tab_config = wx.SplitterWindow(notebook, style=wx.SP_LIVE_UPDATE)
        _sty = wx.BORDER_SUNKEN
        _p1 = wx.Window(_tab_config, style=_sty)
        _p2 = wx.Window(_tab_config, style=_sty)
        self.tree = wx.TreeCtrl(_p1, wx.NewIdRef(), wx.DefaultPosition, wx.DefaultSize, style=wx.TR_DEFAULT_STYLE | wx.TR_FULL_ROW_HIGHLIGHT)
        self.root_item = self.tree.AddRoot("TIA Portal")
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelectConfigTree, self.tree)
        self.tab_config_value: wx.TextCtrl = wx.TextCtrl(_p2, style=wx.TE_WORDWRAP|wx.TE_NO_VSCROLL|wx.TE_READONLY)
        _p1sizer: wx.BoxSizer = wx.BoxSizer(wx.VERTICAL)
        _p1sizer.Add(self.tree, proportion=1, flag=wx.EXPAND|wx.ALL, border=1)
        _p1.SetSizer(_p1sizer)
        _p2sizer: wx.BoxSizer = wx.BoxSizer(wx.VERTICAL)
        _p2sizer.Add(self.tab_config_value, proportion=1, flag=wx.EXPAND|wx.ALL, border=1)
        _p2.SetSizer(_p2sizer)
        _tab_config.SetMinimumPaneSize(100)
        _tab_config.SplitVertically(_p1, _p2, 250)
        _tab_config.SetSashPosition(0)
        notebook.AddPage(_tab_project, "Project")
        notebook.AddPage(_tab_config, "Config")

        logger.setup(self.logs, 10)

        self.SetMinSize((600,480))
        self.Show(True)

    def OnOpen(self, e):
        with wx.FileDialog(self, "Open TIA Portal project config", wildcard= "json (*.json)|*.json", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            self.json_config = fileDialog.GetPath()
            self.textctrl_config.write(self.json_config)

        with open(self.json_config) as file:
            config = json.load(file)
            self.config = config_schema.validate_config(config)
            self.populate_config(self.config)

    def OnSelectDLL(self, e):
        with wx.FileDialog(self, "Open path of Siemens.Engineering.dll", wildcard= "DLL (*.dll)|*.dll", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            self.dll = fileDialog.GetPath()



    def OnClose(self, e):
        self.config = {}
        self.textctrl_config.Clear()
        while self.tree.ItemHasChildren(self.root_item):
            item = self.tree.GetFirstChild(self.root_item)[0]
            self.tree.Delete(item)


    def OnExit(self, e):
        self.Close(True)
        self.Destroy()

    
    def OnSelectConfigTree(self, e):
        item = e.GetItem()
        
        value = self.tree.GetItemData(item)

        if value is not None:
            self.tab_config_value.SetValue(str(value))
        else:
            self.tab_config_value.SetValue("")


    def OnRun(self, e):
        dll = Path(self.dll) 
        if not dll.exists() or not dll.is_file():
            error_message = "Siemens.Engineering.dll path does not exist!"
            dialog = wx.MessageDialog(self, error_message, "Error", wx.OK | wx.ICON_ERROR)
            dialog.ShowModal()
            dialog.Destroy()

            return
        import clr
        from System.IO import DirectoryInfo, FileInfo

        clr.AddReference(dll.as_posix())
        import Siemens.Engineering as SE

        print("TIA Portal Automation Tool")
        print()

        portal.execute(
            SE,
            self.config,
            {
                "DirectoryInfo": DirectoryInfo,
                "FileInfo": FileInfo,
                "enable_ui": True,
            }
        )


    def populate_config(self, config: dict) -> None:
        def add_children(root, children):
            for key, value in children.items():
                child = self.tree.AppendItem(root, str(key))
                if isinstance(value, dict):
                    add_children(child, value)
                elif isinstance(value, list):
                    add_children_as_list(child, value)
                else:
                    self.tree.SetItemData(child, value)

        def add_children_as_list(root, children):
            for index, value in enumerate(children):
                child = self.tree.AppendItem(root, str(index))
                if isinstance(value, dict):
                    add_children(child, value)
                elif isinstance(value, list):
                    add_children_as_list(child, value)
                else:
                    self.tree.SetItemData(child, value)

        add_children(self.root_item, config)

        self.tree.Expand(self.root_item)

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

