from anytree import LightNodeMixin
from collections import defaultdict


class ItemWithSupport:
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
    support = defaultdict(int)
    for row in data:
        for item in row:
            support[item.name] += item.support
    return dict(support)


class FPNode(LightNodeMixin):
    __slots__ = ["name", "value"]

    def __init__(self, name, value, parent=None, children=None):
        super().__init__()
        self.name = name
        self.value = value
        self.parent = parent
        self.children = children if children is not None else []  # Ensure it's always a list


class FPTree:
    def __init__(self, data: list[list[ItemWithSupport]], min_support: int):
        self.m_item_to_node = defaultdict(list)
        self.m_min_support = min_support
        self.m_item_support = get_every_single_support(data)
        self.m_freq_one_item = [
            item for item in self.m_item_support if self.m_item_support[item] >= min_support]
        self.m_freq_one_item.sort(
            key=lambda x: self.m_item_support[x], reverse=True)
        self.root = FPNode("root", 0)

        sorted_data = []
        for row in data:
            sorted_row = sorted(
                [item for item in row if item.name in self.m_freq_one_item],
                key=lambda x: self.m_item_support[x.name],
                reverse=True
            )
            sorted_data.append(sorted_row)

        for row in sorted_data:
            self.insert(row, self.root)

    def insert(self, items: list[ItemWithSupport], node: FPNode):
        if not items:
            return
        child_node = next(
            (child for child in node.children if child.name == items[0].name), None)
        if child_node:
            child_node.value += items[0].support
            self.insert(items[1:], child_node)
        else:
            new_node = FPNode(items[0].name, items[0].support, parent=node)
            self.m_item_to_node[items[0].name].append(new_node)
            self.insert(items[1:], new_node)

    def get_conditional_tree(self, item: str) -> 'FPTree':
        data = []
        for node in self.m_item_to_node[item]:
            path = []
            first_support = node.value
            parent = node.parent
            while parent.name != "root":
                path.append(ItemWithSupport(parent.name, first_support))
                parent = parent.parent
            if path:
                data.append(path[::-1])  # Reverse path order
        return FPTree(data, self.m_min_support)

    def get_freq_mode(self) -> dict[str, int]:
        freq_mode = {}
        for item in self.m_freq_one_item[::-1]:
            freq_mode[item] = self.m_item_support[item]
            con_tree = self.get_conditional_tree(item)
            sub_freq_mode = con_tree.get_freq_mode()
            for sub_item, sub_support in sub_freq_mode.items():
                combined_item = sub_item + ',' + item
                freq_mode[combined_item] = sub_support
        return freq_mode
