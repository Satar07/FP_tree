from anytree import LightNodeMixin, RenderTree
from collections import defaultdict
from itertools import combinations


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
            if line[-2] == ',':
                line = line[:-2]  # Remove extra comma at the end of line
            data.append([ItemWithSupport(s, 1)
                         for s in line.strip().split(',')])
    return data


def get_every_single_support(data: list[list[ItemWithSupport]]) -> dict[str, int]:
    """Get the support count for every single item in the dataset"""
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
        self.m_freq_mode = self.get_freq_mode()

    def insert(self, items: list[ItemWithSupport], node: FPNode):
        """Inserts a list of items into the FP tree"""
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
        """Get the conditional tree for a given item"""
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
        """Get the frequent mode of the dataset"""
        freq_mode = {}
        for item in self.m_freq_one_item[::-1]:
            freq_mode[item] = self.m_item_support[item]
            con_tree = self.get_conditional_tree(item)
            sub_freq_mode = con_tree.get_freq_mode()
            for sub_item, sub_support in sub_freq_mode.items():
                combined_item = sub_item + ',' + item
                combined_item_list = combined_item.split(',')
                combined_item_list.sort(
                    key=lambda x: self.m_item_support[x], reverse=True)
                combined_item = ','.join(combined_item_list)
                freq_mode[combined_item] = sub_support
        return freq_mode


class AssociationRule:
    def __init__(self, antecedent, consequent, support, confidence, lift):
        self.antecedent = antecedent
        self.consequent = consequent
        self.support = support
        self.confidence = confidence
        self.lift = lift

    def __str__(self):
        return f"{self.antecedent} => {self.consequent} (Support: {self.support}, Confidence: {self.confidence:.2f}, Lift: {self.lift:.2f})"


class FPTreeWithRules(FPTree):
    def __init__(self, data: list[list[ItemWithSupport]], min_support: int):
        super().__init__(data, min_support)

    def get_support(self, itemset: list[str]) -> int:
        """Calculates the support of a given itemset"""
        sorted_itemset = sorted(
            itemset, key=lambda x: self.m_item_support[x], reverse=True)
        itemset_str = ','.join(sorted_itemset)
        return self.m_freq_mode.get(itemset_str, 0)

    def generate_association_rules(self, min_confidence: float, min_lift: float) -> list[AssociationRule]:
        """Generate association rules from the frequent itemsets"""
        rules = []
        freq_itemsets = self.get_freq_mode()

        for itemset_str, support in freq_itemsets.items():
            itemset = itemset_str.split(',')

            # Generate all possible non-empty subsets of the itemset
            for size in range(1, len(itemset)):
                for antecedent in combinations(itemset, size):
                    antecedent = list(antecedent)
                    consequent = list(set(itemset) - set(antecedent))

                    # Calculate support for antecedent and consequent
                    antecedent_support = self.get_support(antecedent)
                    consequent_support = self.get_support(consequent)

                    # Calculate confidence and lift
                    if antecedent_support > 0:
                        confidence = support / antecedent_support
                    else:
                        confidence = 0

                    if consequent_support > 0:
                        lift = confidence / \
                            (consequent_support / len(self.m_item_support))
                    else:
                        lift = 0

                    # Only consider rules with sufficient confidence and lift
                    if confidence >= min_confidence and lift >= min_lift:
                        rule = AssociationRule(
                            antecedent=','.join(antecedent),
                            consequent=','.join(consequent),
                            support=support,
                            confidence=confidence,
                            lift=lift
                        )
                        rules.append(rule)

        return rules


# Example usage
if __name__ == "__main__":
    # Assume that 'data.csv' is the input dataset
    data = read_data('INTEGRATED-DATASET.csv')
    min_support = 2  # Minimum support count
    min_confidence = 0.2  # Minimum confidence threshold
    min_lift = 1  # Minimum lift threshold

    tree = FPTreeWithRules(data, min_support)
    print(RenderTree(tree.root).by_attr())
    freq_mode = tree.m_freq_mode
    # top 10 the most frequent itemsets
    for itemset, support in sorted(freq_mode.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"{itemset}: {support}")
    rules = tree.generate_association_rules(min_confidence, min_lift)

    rules.sort(key=lambda x: x.lift, reverse=True)
    for rule in rules[:10]:
        print(rule)
