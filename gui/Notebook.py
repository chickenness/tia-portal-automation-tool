from . import Panel
import wx


class S:
    PAGE_LOGS       = "Logs"
    PAGE_PROJECT    = "Project"
    PAGE_SETTINGS   = "Settings"


def new(parent: wx.Window) -> wx.Notebook:
    notebook: wx.Notebook = wx.Notebook(parent)

    _logs       = Panel.log(notebook)
    _project    = Panel.project(notebook)
    _settings   = Panel.settings(notebook)

    notebook.AddPage(_project,  S.PAGE_PROJECT)
    notebook.AddPage(_logs,     S.PAGE_LOGS)
    notebook.AddPage(_settings, S.PAGE_SETTINGS)
    # parent.SetClientSize(notebook.GetBestSize()) 

    return notebook


