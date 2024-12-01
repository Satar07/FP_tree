from anytree import *


class ItemWithSupport():
    def __init__(self, name: str, support: int):
        self.name = name
        self.support = support

    def __str__(self):
        return f"{self.name}: {self.support}"


def read_data(file: str) -> list[list[ItemWithSupport]]:
    data = []
    with open(file, 'r', encoding="utf-8") as f:
        for line in f:
            data.append([ItemWithSupport(s, 1)
                        for s in line.strip().split(',')])
    return data


def get_every_single_support(data: list[list[ItemWithSupport]]) -> dict[str, int]:
    support = {}
    for row in data:
        for item in row:
            if item.name in support:
                support[item.name] += item.support
            else:
                support[item.name] = item.support
    return support


class FPNode(LightNodeMixin):
    __slots__ = ["name", "value"]

    def __init__(self, name, value, parent=None, children=None):
        super().__init__()
        self.name = name
        self.value = value
        self.parent = parent
        if children:
            self.children = children


class FPTree():
    root = None
    m_freq_one_item = []
    m_item_to_node = {}
    m_min_support = 0
    m_item_support = {}

    def __init__(self, data: list[list[ItemWithSupport]], min_support: int):
        self.m_min_support = min_support
        self.m_item_support = get_every_single_support(data)
        self.m_freq_one_item = [
            item for item in self.m_item_support if self.m_item_support[item] >= min_support]
        self.m_freq_one_item.sort(
            key=lambda x: self.m_item_support[x], reverse=True)

        sorted_data = []
        for row in data:
            sorted_row = sorted(
                [item for item in row if item.name in self.m_freq_one_item],
                key=lambda x: self.m_item_support[x.name],
                reverse=True
            )
            sorted_data.append(sorted_row)

        self.root = FPNode("root", 0)
        for row in sorted_data:
            self.insert(row, self.root)

    def insert(self, items: list[ItemWithSupport], node: FPNode):
        if not items:
            return
        for child in node.children:
            if child.name == items[0].name:
                child.value += items[0].support
                self.insert(items[1:], node=child)
                return
        new_node = FPNode(items[0].name, items[0].support, parent=node)
        if items[0].name not in self.m_item_to_node:
            self.m_item_to_node[items[0].name] = [new_node]
        else:
            self.m_item_to_node[items[0].name].append(new_node)
        self.insert(items[1:], new_node)

    def get_conditional_tree(self, item: str) -> 'FPTree':
        data = []
        for node in self.m_item_to_node[item]:
            path = []
            first_support = node.value
            if node.parent.name == "root":
                continue
            node = node.parent # skip the item itself
            while node.parent.name != "root":
                path.append(ItemWithSupport(node.name, first_support))
                node = node.parent
            data.append(path)
        return FPTree(data, self.m_min_support)

    def get_freq_mode(self) -> dict[str,int]:
        freq_mode = {}
        for item in self.m_freq_one_item[::-1]:
            # dig the mode of item in freq_one_item_set
            freq_mode[item]=self.m_item_support[item]
            con_tree = self.get_conditional_tree(item)
            sub_freq_mode  = con_tree.get_freq_mode()
            # merge
            for (sub_item,sub_support) in sub_freq_mode.items():
                freq_mode[sub_item+','+item] = sub_support
        return freq_mode
        
                
