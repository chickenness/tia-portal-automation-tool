import wx

from . import Splitter, Panel

class S:
    TAB_PROJECT     = "Project"
    TAB_CONFIG      = "Config"

class Notebook(wx.Notebook):
    def __init__(self, parent: wx.Window) -> None:
        wx.Notebook.__init__(self, parent)

def new(parent: wx.Window) -> wx.Notebook:
    notebook: wx.Notebook = Notebook(parent)

    notebook.tab_project = Panel.project(notebook)
    notebook.tab_config = Splitter.new(notebook)

    notebook.AddPage(notebook.tab_project, S.TAB_PROJECT)
    notebook.AddPage(notebook.tab_config, S.TAB_CONFIG)

    return notebook


