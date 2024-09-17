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
        self.root = wx.GetTopLevelParent(self)
        self.root_item = self.AddRoot(root_name)

    def bind(self, cmd):
        self.root.Bind(wx.EVT_TREE_SEL_CHANGED, cmd, self)

    def populate(self, config: Config) -> None:
        data = config.json()
        def add_children(root, children):
            for key, value in children.items():
                child = self.AppendItem(root, str(key))
                if isinstance(value, dict):
                    add_children(child, value)
                elif isinstance(value, list):
                    add_children_as_list(child, value)
                else:
                    self.SetItemData(child, value)

        def add_children_as_list(root, children):
            for index, value in enumerate(children):
                child = self.AppendItem(root, str(index))
                if isinstance(value, dict):
                    add_children(child, value)
                elif isinstance(value, list):
                    add_children_as_list(child, value)
                else:
                    self.SetItemData(child, value)

        add_children(self.root_item, data)

        self.Expand(self.root_item)


def new(parent: wx.Window) -> wx.TreeCtrl:
    tree = Tree(parent, "TIA Portal")
    tree.bind(tree.root.OnSelectConfigTree)

    return tree
