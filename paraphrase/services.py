from itertools import permutations

from nltk import ParentedTree, Tree


def validate_limit(limit: str, is_valid: bool = True):
    try:
        limit = int(limit)
        if not limit > 0:
            is_valid = False
    except ValueError:
        is_valid = False
    return limit, is_valid


def _check_np_label(subtree):
    """
    Checks whether the value is a noun phrase ("NP") and its right sibling (if
    there is one) is a tag ("," or "CC")
    """
    if subtree.label() != "NP":
        return False
    rs = subtree.right_sibling()
    if rs:
        return _check_tag_label(rs)
    return True


def _check_tag_label(subtree):
    """
    Checks whether the value is a tag ("," or "CC") and its right sibling is a
    noun phrase ("NP")
    """
    if subtree.label() not in [",", "CC"]:
        return False
    rs = subtree.right_sibling()
    if rs:
        return _check_np_label(rs)
    return False


def _check_siblings(subtree):
    """
    Checks whether value and its siblings are noun phrases ("NP")
    or tags ("," or "CC") with the help of '_check_label' function.
    In order to use the nodes only once, the ones with left siblings are
    filtered out because they were previously checked. Or one of their left
    siblings didn't match, so this group is discarded.
    """
    if subtree.left_sibling():
        return False
    return _check_np_label(subtree)


def _index_neighbours(subtree, np_indexes):
    rs = subtree.right_sibling()
    if not rs:
        return np_indexes
    if rs.label() == "NP":
        np_indexes.append(rs.treeposition())
    return _index_neighbours(rs, np_indexes)


def _create_np_indexes_list(parented_tree):
    np_indexes_list = []
    for subtree in parented_tree.subtrees(filter=_check_siblings):
        np_indexes = [subtree.treeposition()]
        np_indexes = _index_neighbours(subtree, np_indexes)
        np_indexes_list.append(tuple(np_indexes))
    return np_indexes_list


def _flatten_tree(tree):
    return ' '.join(str(tree).split())


def _create_variation(parented_tree, index_tuple, permutation):
    tree = Tree.fromstring(parented_tree)
    tree_copy = tree.copy(deep=True)
    for i in range(len(index_tuple)):
        tree[index_tuple[i]] = tree_copy[permutation[i]]
    return _flatten_tree(tree)


def _create_tree_permutations(flat_tree, np_indexes_list, limit):
    tree_set = {flat_tree}
    for index_tuple in np_indexes_list:
        for tree in tree_set.copy():
            for perm in permutations(index_tuple):
                if perm != index_tuple:
                    tree_permutation = _create_variation(tree, index_tuple, perm)
                    tree_set.add(tree_permutation)
                    if len(tree_set) > limit:
                        return tree_set
    return tree_set


def create_tree_variations(tree_serializer, limit) -> list:
    flat_tree = tree_serializer.data["tree"]
    ptree = ParentedTree.fromstring(flat_tree)
    np_indexes_list = _create_np_indexes_list(ptree)
    flat_tree = _flatten_tree(ptree)
    tree_set = _create_tree_permutations(flat_tree, np_indexes_list, limit)
    tree_set.discard(flat_tree)

    return [{"tree": tree_string} for tree_string in list(tree_set)[:limit]]
