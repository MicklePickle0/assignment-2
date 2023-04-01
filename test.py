import unittest

import os
import pytest
from hypothesis import given
from hypothesis.strategies import integers
from typing import Tuple
from tm_trees import DIRECTORYTREE_EXAMPLE_RESULT, FileTree, TMTree, \
    DirectoryTree, dir_tree_from_nested_tuple, path_to_nested_tuple, \
    ChessTree, get_worksheet_tree, moves_to_nested_dict, \
    OperationNotSupportedError

# This should be the path to the "workshop" directory in the sample data
# included in the zip file for this assignment.
EXAMPLE_PATH = os.path.join('example-directory', 'workshop')


##############################################################################
# Helpers
##############################################################################


def is_valid_colour(colour: Tuple[int, int, int]) -> bool:
    """
    Return True iff <colour> is a valid colour. That is, if all of its
    values are between 0 and 255, inclusive.
    """
    for i in range(3):
        if not 0 <= colour[i] <= 255:
            return False
    return True


###########################################
# TMTree testing
###########################################


class TestTMTree:
    def test_init_doctest(self) -> None:
        t1 = TMTree('B', [], 5)
        assert t1.rect is None
        assert t1.data_size == 5
        t2 = TMTree('A', [t1], 1)
        assert t2.rect is None
        assert t2.data_size == 6

    def test_init_no_subtree(self) -> None:
        t1 = TMTree('A', [], 3)
        assert t1.rect is None
        assert t1.data_size == 3

    def test_init_one_subtree(self) -> None:
        t1 = TMTree('A', [], 3)
        t2 = TMTree('B', [t1], 2)
        assert t2.rect is None
        assert t2.data_size == 5

    def test_init_multiple_subtree(self) -> None:
        t1 = TMTree('A', [], 3)
        t2 = TMTree('B', [t1], 2)
        t3 = TMTree('C', [t1, t2], 1)
        assert t3.rect is None
        assert t3.data_size == 9

    def test_init_subtree_has_parent(self) -> None:
        t1 = TMTree('A', [], 3)
        t2 = TMTree('B', [t1], 2)
        t4 = TMTree('D', [t2])
        assert t2._parent_tree is t4


class TestDisplayedTreeLeaf:
    def test_is_displayed_tree_leaf_doctest(self) -> None:
        t1 = TMTree('B', [], 5)
        assert t1.is_displayed_tree_leaf()
        t2 = TMTree('A', [t1], 1)
        assert t1.is_displayed_tree_leaf()
        assert not t2.is_displayed_tree_leaf()

    def test_is_displayed_tree_leaf_no_subtree(self) -> None:
        t1 = TMTree('A', [], 3)
        assert t1.is_displayed_tree_leaf() == True

    def test_is_displayed_tree_leaf_one_subtree(self) -> None:
        t1 = TMTree('A', [], 3)
        t2 = TMTree('B', [t1], 2)
        assert t1.is_displayed_tree_leaf() == True
        assert t2.is_displayed_tree_leaf() == False

    def test_is_displayed_tree_leaf_multiple_subtree(self) -> None:
        t1 = TMTree('A', [], 3)
        t2 = TMTree('B', [t1], 2)
        t3 = TMTree('C', [t1, t2], 1)
        assert t1.is_displayed_tree_leaf() == True
        assert t2.is_displayed_tree_leaf() == False
        assert t3.is_displayed_tree_leaf() == False

    def test_is_displayed_tree_leaf_has_parent(self) -> None:
        t1 = TMTree('A', [], 3)
        t2 = TMTree('B', [t1], 2)
        t4 = TMTree('D', [t2])
        t3 = TMTree('C', [t1, t2], 1)
        assert t1.is_displayed_tree_leaf() == True
        assert t2.is_displayed_tree_leaf() == False
        assert t3.is_displayed_tree_leaf() == False
        assert t4.is_displayed_tree_leaf() == False

    def test_get_path_string_no_ancestor(self) -> None:
        t1 = TMTree('A', [], 3)
        assert t1.get_path_string() == 'A(3) None'

    def test_get_path_string_one_ancestor(self) -> None:
        t1 = TMTree('A', [], 3)
        t2 = TMTree('B', [t1], 2)
        assert t1.get_path_string() == 'B | A(3) None'

    def test_get_path_string_multiple_ancestors(self) -> None:
        t1 = TMTree('A', [], 3)
        t2 = TMTree('B', [t1], 2)
        t3 = TMTree('C', [t2], 1)
        assert t1.get_path_string() == 'C | B | A(3) None'

    def test_get_path_string_no_data_no_rect(self) -> None:
        t4 = TMTree('D', [], 0)
        assert t4.get_path_string() == 'D(0) None'

    def test_get_path_string_with_data_rect_multiple_ancestors(self) -> None:
        t1 = TMTree('A', [], 3)
        t2 = TMTree('B', [t1], 2)
        t3 = TMTree('C', [t2], 1)
        t4 = TMTree('D', [], 0)
        t5 = TMTree('E', [t4, t3], 4)
        assert t5.rect == None
        assert t4.get_path_string() == \
               'E | D(0) None'

    def test_get_path_string_doctest(self) -> None:
        d1 = TMTree('C1', [], 5)
        d2 = TMTree('C2', [d1], 1)
        d3 = TMTree('C', [d2], 1)
        assert d3.get_path_string() == 'C(7) None'
        assert d1.get_path_string() == 'C | C2 | C1(5) None'

    def test_update_rectangles_doctest(self) -> None:
        t1 = TMTree('B', [], 5)
        t2 = TMTree('A', [t1], 1)
        t2.update_rectangles((0, 0, 100, 200))
        assert t2.rect == (0, 0, 100, 200)
        assert t1.rect == (0, 0, 100, 200)
        s1 = TMTree('C1', [], 5)
        s2 = TMTree('C2', [], 15)
        t3 = TMTree('C', [s1, s2], 1)
        t3.update_rectangles((0, 0, 100, 200))
        assert s1.rect == (0, 0, 100, 50)
        assert s2.rect == (0, 50, 100, 150)
        assert t3.rect == (0, 0, 100, 200)

    def test_update_rectangles(self) -> None:
        t1 = TMTree('A', [], 5)
        t2 = TMTree('B', [t1], 2)
        t2.update_rectangles((0, 0, 100, 200))
        assert t2.rect == (0, 0, 100, 200)
        assert t1.rect == (0, 0, 100, 200)

        s1 = TMTree('C1', [], 15)
        s2 = TMTree('C2', [], 5)
        t3 = TMTree('C', [s1, s2], 1)
        t3.update_rectangles((0, 0, 200, 100))
        assert s1.rect == (0, 0, 150, 100)
        assert s2.rect == (150, 0, 50, 100)
        assert t3.rect == (0, 0, 200, 100)

        u1 = TMTree('D1', [], 1)
        u2 = TMTree('D2', [], 2)
        u3 = TMTree('D3', [u1, u2], 3)
        u4 = TMTree('D4', [u3], 4)
        u4.update_rectangles((0, 0, 200, 100))
        assert u4.rect == (0, 0, 200, 100)
        assert u3.rect == (0, 0, 200, 100)
        assert u1.rect == (0, 0, 66, 100)
        assert u2.rect == (66, 0, 133, 100)

    def test_get_rectangles_doctest(self) -> None:
        t1 = TMTree('B', [], 5)
        t2 = TMTree('A', [t1], 1)
        t2.update_rectangles((0, 0, 100, 200))
        assert t2.get_rectangles()[0][0] == (0, 0, 100, 200)
        s1 = TMTree('C1', [], 5)
        s2 = TMTree('C2', [], 15)
        t3 = TMTree('C', [s1, s2], 1)
        t3.update_rectangles((0, 0, 100, 200))
        rectangles = t3.get_rectangles()
        assert rectangles[0][0] == (0, 0, 100, 50)
        assert rectangles[1][0] == (0, 50, 100, 150)

    def test_get_rectangles_no_rect(self) -> None:
        t1 = TMTree('B', [], 5)
        t2 = TMTree('A', [t1], 1)
        assert t2.get_rectangles() == []

    def test_get_rectangles_multiple_leaves(self) -> None:
        t1 = TMTree('B', [], 5)
        t2 = TMTree('A', [t1], 1)
        s1 = TMTree('C1', [], 5)
        s2 = TMTree('C2', [], 15)
        t3 = TMTree('C', [s1, s2], 1)
        t3.update_rectangles((0, 0, 100, 200))
        rectangles = t3.get_rectangles()
        assert len(rectangles) == 2
        assert rectangles[0][0] == (0, 0, 100, 50)
        assert rectangles[1][0] == (0, 50, 100, 150)

    def test_get_rectangles_nested_subtrees(self) -> None:
        ss2 = TMTree('k', [], 5)
        ss1 = TMTree('j', [], 10)
        s5 = TMTree('i', [], 2)
        s4 = TMTree('h', [], 4)
        s3 = TMTree('g', [], 4)
        s2 = TMTree('f', [], 5)
        s1 = TMTree('e', [ss1, ss2], 5)

        t4 = TMTree('d', [], 10)
        t3 = TMTree('c', [s3, s4, s5], 5)
        t2 = TMTree('b', [s1, s2], 5)
        t1 = TMTree('a', [t2, t3, t4], 5)

        t1.update_rectangles((0, 0, 55, 30))
        rectangles = t1.get_rectangles()
        assert len(rectangles) == 7

        assert rectangles[0][0] == (0, 0, 19, 24)
        assert rectangles[1][0] == (19, 0, 9, 24)
        assert rectangles[2][0] == (0, 24, 29, 6)
        assert rectangles[3][0] == (29, 0, 14, 12)
        assert rectangles[4][0] == (29, 12, 14, 12)
        assert rectangles[5][0] == (29, 24, 14, 6)
        assert rectangles[6][0] == (43, 0, 10, 30)

    def test_get_tree_at_position(self) -> None:
        # Create example trees
        t1 = TMTree('B', [], 5)
        t2 = TMTree('A', [t1], 1)
        s1 = TMTree('C1', [], 5)
        s2 = TMTree('C2', [], 15)
        t3 = TMTree('C', [s1, s2], 1)

        # Update rectangles for each tree
        t2.update_rectangles((0, 0, 100, 200))
        t3.update_rectangles((0, 0, 100, 200))

        # Test cases
        assert t1.get_tree_at_position((10, 10)) is t1
        assert t2.get_tree_at_position((10, 10)) is t1
        assert t2.get_tree_at_position((500, 500)) is None
        assert t3.get_tree_at_position((0, 0)) is s1
        assert t3.get_tree_at_position((100, 100)) is s2

    def test_expand(self) -> None:
        # Create example trees
        s1 = TMTree('C1', [], 5)
        s2 = TMTree('C2', [], 15)
        t3 = TMTree('C', [s1, s2], 1)

        # Set initial expanded state
        t3._expanded = False

        # Test cases
        assert s1.is_displayed_tree_leaf() is False
        assert t3.expand() is s1
        assert s1.is_displayed_tree_leaf() is True
        assert t3._expanded is True

        # Test case for leaf node
        t4 = TMTree('D', [], 1)
        t4._expanded = False
        assert t4.expand() is t4
        assert t4._expanded is False

    def test_expand_all_with_no_subtrees(self) -> None:
        leaf = TMTree('A', [], 5)
        leaf._expanded = False
        assert leaf.expand_all() is leaf

    def test_expand_all_with_one_subtree(self) -> None:
        sub = TMTree('B', [], 10)
        root = TMTree('A', [sub], 5)
        root._expanded = False
        sub._expanded = False
        assert root.expand_all() is sub
        assert sub.is_displayed_tree_leaf()
        assert not root.is_displayed_tree_leaf()

    def test_expand_all_with_multiple_subtrees(self) -> None:
        s1 = TMTree('C1', [], 5)
        s2 = TMTree('C2', [], 15)
        s3 = TMTree('C3', [], 10)
        t1 = TMTree('B', [s1, s2], 20)
        t2 = TMTree('D', [s3], 10)
        root = TMTree('A', [t1, t2], 5)
        root._expanded = False
        t1._expanded = False
        t2._expanded = False
        assert root.expand_all() is s3
        assert s1.is_displayed_tree_leaf()
        assert s2.is_displayed_tree_leaf()
        assert s3.is_displayed_tree_leaf()
        assert not t1.is_displayed_tree_leaf()
        assert not t2.is_displayed_tree_leaf()
        assert not root.is_displayed_tree_leaf()

    def test_collapse_leaf(self) -> None:
        t1 = TMTree('leaf', [], 1)
        assert t1.collapse() is t1

    def test_collapse_single_subtree(self) -> None:
        t1 = TMTree('C1', [], 5)
        t2 = TMTree('C2', [t1], 1)
        assert t1.collapse() is t2
        assert t1.is_displayed_tree_leaf() is False
        assert t2.is_displayed_tree_leaf() is True

    def test_collapse_multiple_subtrees(self) -> None:
        t1 = TMTree('C1', [], 5)
        t2 = TMTree('C2', [], 15)
        t3 = TMTree('C3', [t1, t2], 1)
        t4 = TMTree('C4', [t3], 10)
        assert t2.collapse() is t3
        assert t2.is_displayed_tree_leaf() is False
        assert t1.is_displayed_tree_leaf() is False
        assert t3.is_displayed_tree_leaf() is True
        assert t4.is_displayed_tree_leaf() is False

    def test_collapse_all(self) -> None:
        d1 = TMTree('C1', [], 5)
        d2 = TMTree('C2', [d1], 1)
        d3 = TMTree('C', [d2], 1)
        assert d1.is_displayed_tree_leaf()
        assert d1.collapse_all() is d3
        assert not d1.is_displayed_tree_leaf()
        assert not d2.is_displayed_tree_leaf()
        assert d3.is_displayed_tree_leaf()

        d1 = TMTree('C1', [], 5)
        d2 = TMTree('C2', [d1], 1)
        d3 = TMTree('C', [d2], 1)
        d4 = TMTree('D', [], 1)
        d5 = TMTree('E', [d4], 1)
        d6 = TMTree('F', [d5], 1)
        d7 = TMTree('G', [d3, d6], 1)
        assert d1.is_displayed_tree_leaf()
        assert d4.is_displayed_tree_leaf()
        assert d1.collapse_all() is d7
        assert not d1.is_displayed_tree_leaf()
        assert not d2.is_displayed_tree_leaf()
        assert not d4.is_displayed_tree_leaf()
        assert not d5.is_displayed_tree_leaf()
        assert not d6.is_displayed_tree_leaf()
        assert d7.is_displayed_tree_leaf()

        d1 = TMTree('C1', [], 5)
        d2 = TMTree('C2', [d1], 1)
        d3 = TMTree('C', [d2], 1)
        d4 = TMTree('D', [], 1)
        d5 = TMTree('E', [d4], 1)
        d6 = TMTree('F', [d5], 1)
        d7 = TMTree('G', [d3, d6], 1)
        assert d1.is_displayed_tree_leaf()
        assert d4.is_displayed_tree_leaf()
        assert d4.collapse_all() is d7
        assert not d1.is_displayed_tree_leaf()
        assert not d2.is_displayed_tree_leaf()
        assert not d4.is_displayed_tree_leaf()
        assert not d5.is_displayed_tree_leaf()
        assert not d6.is_displayed_tree_leaf()
        assert d7.is_displayed_tree_leaf()

    def test_move_simple(self) -> None:
        s1 = TMTree('C1', [], 5)
        s2 = TMTree('C2', [], 15)
        t3 = TMTree('C', [s1, s2], 1)
        t3.update_rectangles((0, 0, 100, 200))

        assert s1.is_displayed_tree_leaf() == True
        assert s2.is_displayed_tree_leaf() == True

        s2.move(s1)

        assert s2.rect == (0, 0, 100, 200)
        assert s1.data_size == 20
        assert t3.data_size == 21
        assert t3.get_tree_at_position((0, 0)) is s2
        assert s1.is_displayed_tree_leaf() == False
        assert s2.is_displayed_tree_leaf() == True

    def test_move_same_parent(self) -> None:
        s1 = TMTree('C1', [], 5)
        s2 = TMTree('C2', [], 15)
        t3 = TMTree('C', [s1, s2], 1)
        t3.update_rectangles((0, 0, 100, 200))

        s2.move(s1)

        assert s2.rect == (0, 0, 100, 200)
        assert s1.data_size == 20
        assert t3.data_size == 21
        assert t3.get_tree_at_position((0, 0)) is s2
        assert not s1.is_displayed_tree_leaf()
        assert s2.is_displayed_tree_leaf()

    def test_change_size(self) -> None:
        s1 = TMTree('C1', [], 5)
        s2 = TMTree('C2', [], 15)
        t3 = TMTree('C', [s1, s2], 1)
        t3.update_rectangles((0, 0, 100, 200))
        assert s2.data_size == 15
        assert t3.data_size == 21
        assert s2.rect == (0, 50, 100, 150)
        s2.change_size(-2/3)
        assert s2.data_size == 5
        assert t3.data_size == 11
        assert s2.rect == (0, 100, 100, 100)
        s2.change_size(0.5)
        assert s2.data_size == 8
        assert t3.data_size == 14
        assert s2.rect == (0, 76, 100, 123)

    def test_change_size_multiple_updates(self) -> None:
        s1 = TMTree('C1', [], 5)
        s2 = TMTree('C2', [], 15)
        t3 = TMTree('C', [s1, s2], 1)
        t3.update_rectangles((0, 0, 100, 200))
        s1.change_size(0.5)
        assert s1.data_size == 8
        assert s2.data_size == 15
        assert t3.data_size == 24
        s2.change_size(-0.5)
        assert s2.data_size == 7
        assert t3.data_size == 16
        s1.change_size(-0.5)
        assert s1.data_size == 4
        assert t3.data_size == 12


if __name__ == '__main__':
    unittest.main()
