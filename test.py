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


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here


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
        ss2 = TMTree('k', [], 10)
        ss1 = TMTree('j', [], 10)
        s5 = TMTree('i', [], 3)
        s4 = TMTree('h', [], 6)
        s3 = TMTree('g', [], 6)
        s2 = TMTree('f', [], 5)
        s1 = TMTree('e', [ss1, ss2], 20)

        t4 = TMTree('d', [], 10)
        t3 = TMTree('c', [s3, s4, s5], 15)
        t2 = TMTree('b', [s1, s2], 25)
        t1 = TMTree('a', [t2, t3, t4], 55)

        t1.update_rectangles((0, 0, 55, 30))
        rectangles = t1.get_rectangles()
        assert len(rectangles) == 7
        print(rectangles[0][0])
        print(rectangles[1][0])
        print(rectangles[2][0])
        print(rectangles[3][0])
        print(rectangles[4][0])
        print(rectangles[5][0])
        print(rectangles[6][0])

        assert rectangles[0][0] == (0, 0, 20, 24)
        assert rectangles[1][0] == (20, 0, 10, 24)
        assert rectangles[2][0] == (0, 24, 30, 6)
        assert rectangles[3][0] == (30, 0, 15, 12)
        assert rectangles[4][0] == (30, 12, 15, 12)
        assert rectangles[5][0] == (30, 24, 15, 6)
        assert rectangles[6][0] == (45, 0, 10, 30)


    #def get_tree_at_position(self) -> None:


if __name__ == '__main__':
    unittest.main()
