from main import *


def test_read_data():
    data = read_data('book.csv')
    assert data[0] == ["薯片", "鸡蛋", "面包", "牛奶"]


def test_get_every_single_support():
    data = read_data('book.csv')
    support = get_every_single_support(data)
    assert support["薯片"] == 7
    assert support["鸡蛋"] == 7


def test_get_PFTree():
    data = read_data('book.csv')
    tree = FPTree(data, min_support=3)
    assert tree.root.children[0].name == "薯片"
    assert tree.root.children[0].value == 7
    assert tree.freq_one_item == ["薯片", "鸡蛋", "面包", "牛奶", "啤酒"]


def test_get_freq_mode():
    data = read_data('book.csv')
    freq_mode = get_freq_mode(data, min_support=3)
    assert freq_mode.get("薯片") == 7
    assert freq_mode.get("薯片，鸡蛋") == 6