from lib.pp import pp
from gui import MenuBar, FileDialog, Notebook
from pathlib import Path
import wx

class S:
    MENU_NAME_FILE          = "&File"
    MENU_NAME_RUN           = "&Action"
    MENU_NAME_OPEN          = "&Open"
    MENU_DESC_OPEN          = " Open project configuration."
    MENU_NAME_CLOSE         = "&Close"
    MENU_DESC_CLOSE         = " Close current configuration."
    MENU_NAME_EXIT          = "&Exit"
    MENU_DESC_EXIT          = "Terminate this tool. (Does not close TIA Portal)"
    MENU_NAME_RUN           = "&Run"
    MENU_DESC_RUN           = " Run project."
    NB_TAB_PROJECT          = "Project"
    NB_TAB_CONFIG           = "Config"
    LABEL_BROWSE            = "Browse"
    LABEL_EXECUTE           = "Execute"
    TEXT_BROWSE             = "Browse project config"
    SIZE_BROWSE             = (300, -1)
    FLAG_SIZER_H            = wx.ALL|wx.EXPAND
    FLAG_SIZER_V            = wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP
    FLAG_SIZER_TREE         = wx.ALL|wx.EXPAND
    BORDER                  = 5
    BORDER_TREE             = 1
    STYLE_WINDOW            = wx.BORDER_SUNKEN
    STYLE_TREE              = wx.TR_DEFAULT_STYLE | wx.TR_FULL_ROW_HIGHLIGHT
    NAME_ROOT               = "TIA Portal"



class MainWindow(wx.Frame):
    def __init__(self, parent, title) -> None:
        wx.Frame.__init__(self, parent, title=title, size=(800,600))
        self.portal: pp.Portal = None

        self.CreateStatusBar()


        # Menubars and menu items
        menubar: wx._core.MenuBar = wx.MenuBar()
        _filemenu = wx.Menu()
        _open = _filemenu.Append(wx.ID_OPEN, S.MENU_NAME_OPEN, S.MENU_DESC_OPEN)
        _close = _filemenu.Append(wx.ID_CLOSE, S.MENU_NAME_CLOSE, S.MENU_DESC_CLOSE)
        _filemenu.AppendSeparator()
        _exit = _filemenu.Append(wx.ID_EXIT, S.MENU_NAME_EXIT, S.MENU_DESC_EXIT)
        _runmenu = wx.Menu()
        _run = _runmenu.Append(wx.NewIdRef(), S.MENU_NAME_RUN, S.MENU_DESC_RUN)
        self.Bind(wx.EVT_MENU, self.OnOpen, _open)
        self.Bind(wx.EVT_MENU, self.OnExit, _exit)
        self.Bind(wx.EVT_MENU, self.OnClose, _close)
        self.Bind(wx.EVT_MENU, self.OnRun, _run)
        menubar.Append(_filemenu, S.MENU_NAME_FILE)
        menubar.Append(_runmenu, S.MENU_NAME_RUN)
        self.SetMenuBar(menubar)


        # Notebook, 2 tabs: Project and Config
        notebook: wx.Notebook = wx.Notebook(self)
        _tab_project = wx.Panel(notebook)
        _vsizer = wx.BoxSizer(wx.VERTICAL)
        _hsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.config_path = wx.TextCtrl(_tab_project, size=S.SIZE_BROWSE)
        _browse = wx.Button(_tab_project, label=S.LABEL_BROWSE)
        _execute = wx.Button(_tab_project, label=S.LABEL_EXECUTE)
        _hsizer.Add(self.config_path, proportion=1, flag=S.FLAG_SIZER_H, border=S.BORDER)
        _hsizer.Add(_browse, flag=wx.ALL, border=S.BORDER)
        _hsizer.Add(_execute, flag=wx.ALL, border=S.BORDER)
        _vsizer.Add(_hsizer, flag=S.FLAG_SIZER_V, border=S.BORDER)
        _tab_project.SetSizer(_vsizer)
        self.Bind(wx.EVT_BUTTON, self.OnOpen, _browse)
        _tab_config = wx.SplitterWindow(notebook, style=wx.SP_LIVE_UPDATE)
        _p1 = wx.Window(_tab_config, style=S.STYLE_WINDOW)
        _p2 = wx.Window(_tab_config, style=S.STYLE_WINDOW)
        self.tree = wx.TreeCtrl(_p1, wx.NewIdRef(), wx.DefaultPosition, wx.DefaultSize, style=S.STYLE_TREE)
        _root = self.tree.AddRoot(S.NAME_ROOT)
        _p1sizer = wx.BoxSizer(wx.VERTICAL)
        _p1sizer.Add(self.tree, proportion=1, flag=S.FLAG_SIZER_TREE, border=S.BORDER_TREE)
        _p1.SetSizer(_p1sizer)
        _tab_config.SetMinimumPaneSize(150)
        _tab_config.SplitVertically(_p1, _p2, 250)
        _tab_config.SetSashPosition(0)
        notebook.AddPage(_tab_project, S.NB_TAB_PROJECT)
        notebook.AddPage(_tab_config, S.NB_TAB_CONFIG)


        self.SetMinSize((600,480))

        self.Show(True)


    def OnOpen(self, e):
        filepath = FileDialog.open_config(self)
        if not filepath:
            return
        try:
            self.portal = pp.parse(filepath)
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


if __name__ == '__main__':
    app = wx.App(False)
    frame = MainWindow(None, title="TIA Portal Automation Tool")
    app.MainLoop()


