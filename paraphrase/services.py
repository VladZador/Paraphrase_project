from nltk import Tree, ParentedTree


def validate_limit(limit: str, is_valid: bool = True):
    try:
        limit = int(limit)
        if not limit > 0:
            is_valid = False
    except ValueError:
        is_valid = False
    return limit, is_valid


def create_tree_variations(tree_serializer, limit) -> list:
    tree_list = [tree_serializer.data]
    tree = Tree.fromstring(tree_serializer.data["tree"])
    ptree = ParentedTree.convert(tree)
    for subtree in ptree.subtrees():
        print(subtree)
        print('  Left Sibling  = %s' % subtree.left_sibling())
        print('  Right Sibling = %s' % subtree.right_sibling())
    return tree_list
