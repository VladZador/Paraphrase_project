from itertools import permutations

from nltk import ParentedTree, Tree


def validate_limit(limit: str):
    """Checks that the limit is a positive integer by converting it

    :param limit: limit on the number of generated tree variations
    :return: a tuple containing the converted integer (or original string)
    limit and a boolean used to describe whether limit is valid
    """

    is_valid = True
    try:
        limit = int(limit)
        if not limit > 0:
            is_valid = False
    except ValueError:
        is_valid = False
    return limit, is_valid


def _check_np_label(subtree: ParentedTree) -> bool:
    """
    Checks whether the value of the current subtree is a noun phrase ("NP")
    and whether its right sibling (if any) is a tag ("," or "CC")
    """

    if subtree.label() != "NP":
        return False
    rs = subtree.right_sibling()
    if rs:
        return _check_tag_label(rs)
    return True


def _check_tag_label(subtree: ParentedTree) -> bool:
    """
    Checks whether the value of the current subtree is a tag ("," or "CC")
    and whether its right sibling is a noun phrase ("NP")
    """

    if subtree.label() not in [",", "CC"]:
        return False
    rs = subtree.right_sibling()
    if rs:
        return _check_np_label(rs)
    return False


def _check_siblings(subtree: ParentedTree) -> bool:
    """
    Checks whether value and its siblings are alternating noun phrases ("NP")
    and tags ("," or "CC")

    The function uses the "_check_label" function which in turn uses
    the "_check_tag" function.

    In order to use the nodes only once, the ones with left siblings are
    filtered out because they were previously checked. Or one of their left
    siblings didn't match, so this group is discarded.
    """

    if subtree.left_sibling():
        return False
    return _check_np_label(subtree)


def _index_siblings(subtree: ParentedTree, np_indexes: list) -> list:
    """
    Creates a list of tuples indicating the position of noun phrases
    ("NP") relative to the root

    The first time the function is called, a list with a tuple with the
    position of the first tree node must be passed to the function. And
    then tuples with positions of noun phrases ("NP") of siblings of the
    node will be added to this list

    :param subtree: current subtree
    :param np_indexes: list of tuples with positions of already processed
     tree nodes
    :return: list of tuples with positions of processed tree nodes
    """

    rs = subtree.right_sibling()
    if not rs:
        return np_indexes
    if rs.label() == "NP":
        np_indexes.append(rs.treeposition())
    return _index_siblings(rs, np_indexes)


def _create_np_indexes_list(parented_tree: ParentedTree) -> list:
    """
    Creates a list of tuples of tuples with noun phrase ("NP")
    positions of the tree
    """

    np_indexes_list = []
    for subtree in parented_tree.subtrees(filter=_check_siblings):
        np_indexes = [subtree.treeposition()]
        np_indexes = _index_siblings(subtree, np_indexes)
        np_indexes_list.append(tuple(np_indexes))
    return np_indexes_list


def _flatten_tree(tree):
    """
    Flattens the tree

    :param tree: Tree or ParentedTree instance
    :return: string representation of the given tree
    """

    return ' '.join(str(tree).split())


def _create_variation(flat_tree: str,
                      index_tuple: tuple,
                      permutation: tuple) -> str:
    """
    Creates a flat tree variation of the given flat tree

    Creates a tree variation by replacing nodes at the positions
    specified by the "index_tuple" parameter with nodes at the
    positions specified by the "permutation" parameter
    """

    tree = Tree.fromstring(flat_tree)
    tree_copy = tree.copy(deep=True)
    for i in range(len(index_tuple)):
        tree[index_tuple[i]] = tree_copy[permutation[i]]
    return _flatten_tree(tree)


def _create_tree_permutations(flat_tree: str,
                              np_indexes_list: list,
                              limit: int) -> list:
    """Creates a list with flat tree variations of the given tree

    :param flat_tree: a string representation of the tree
    :param np_indexes_list: a list of tuples of tuples with noun phrase
     ("NP") positions of the tree
    :param limit: limit on the number of tree variations to generate
    :return: a list with flat tree variations
    """

    tree_vars = [flat_tree]
    for index_tuple in np_indexes_list:
        for tree in tree_vars.copy():
            for perm in permutations(index_tuple):
                if perm != index_tuple:
                    tree_variation = _create_variation(tree, index_tuple, perm)
                    tree_vars.append(tree_variation)
                    if len(tree_vars) > limit:
                        return tree_vars
    return tree_vars


def create_tree_variations(flat_tree: str,
                           limit: int) -> list:
    """
    Creates a list with variation representations of the given tree

    :param flat_tree: a string representation of the tree
    :param limit: limit on the number of tree variations to generate
    :return: a list with {"tree": tree_variation_string} dictionaries
    """

    ptree = ParentedTree.fromstring(flat_tree)
    np_indexes_list = _create_np_indexes_list(ptree)

    # flat_tree is redeclared to have consistent tree representations
    flat_tree = _flatten_tree(ptree)
    tree_vars = _create_tree_permutations(flat_tree, np_indexes_list, limit)
    tree_vars.remove(flat_tree)
    return [{"tree": tree_string} for tree_string in list(tree_vars)[:limit]]
