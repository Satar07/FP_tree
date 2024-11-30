from anytree import *


def read_data(file: str) -> list[list[str]]:
    data = []
    with open(file, 'r', encoding="utf-8") as f:
        for line in f:
            data.append(line.strip().split(','))
    return data #TODO return (data, support)


def get_every_single_support(data: list[list[str]], prev_support=None) -> dict[str, int]:
    support = {}
    for i in range(len(data)):
        for item in data[i]:
            if item in support:
                support[item] += 1 if prev_support is None else prev_support[i]
            else:
                support[item] = 1 if prev_support is None else prev_support[i]
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
    freq_one_item = []
    item_to_node = {}

    def __init__(self, data: list[list[str]], min_support: int, prev_support=None):
        support = get_every_single_support(data, prev_support)
        self.freq_one_item = [
            item for item in support if support[item] >= min_support]
        self.freq_one_item.sort(key=lambda x: support[x], reverse=True)

        sorted_data = []
        for items in data:
            row = []
            for item in self.freq_one_item:
                if item in items:
                    row.append(item)
            sorted_data.append(row)

        self.root = FPNode("root", 0)
        for row in sorted_data:
            self.insert(row, self.root)

    def insert(self, items: list[str], node: FPNode):
        if not items:
            return
        for child in node.children:
            if child.name == items[0]:
                child.value += 1
                self.insert(items[1:], node=child)
                return
        new_node = FPNode(items[0], 1, parent=node)
        if items[0] not in self.item_to_node:
            self.item_to_node[items[0]] = [new_node]
        else:
            self.item_to_node[items[0]].append(new_node)
        self.insert(items[1:], new_node)


def get_freq_mode(data: list[list[str]], min_support: int) -> dict[str, int]:
    tree = FPTree(data, min_support)
    freq_mode = {}
    for item in tree.freq_one_item:
        freq_mode[item] = tree.root.children[item].value
    return freq_mode
