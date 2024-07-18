from __future__ import annotations
import wx


class Tree(wx.TreeCtrl):
    def __init__(self, parent: wx.Window, root_name: str) -> None:
        wx.TreeCtrl.__init__(self, parent,
                             wx.NewIdRef(),
                             wx.DefaultPosition,
                             wx.DefaultSize,
                             style=wx.TR_DEFAULT_STYLE | wx.TR_FULL_ROW_HIGHLIGHT
                             )
        self.root = self.AddRoot(root_name)

    def populate(self, config: dict[str, Any]) -> None:

        for x in range(15):
            child = self.AppendItem(self.root, "Item %d" % x)
            self.SetItemData(child, None)
            for x in range(5):
                child2 = self.AppendItem(child, "Item %d" % x)
                self.SetItemData(child2, None)
        self.Expand(self.root)


def new(parent: wx.Window) -> wx.TreeCtrl:
    tree = Tree(parent, "TIA Portal")

    return tree
