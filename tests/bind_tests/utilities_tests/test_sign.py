from itertools import permutations

from _martinez import (Point,
                       sign)
from hypothesis import given

from tests.utils import (is_even_permutation,
                         permute)
from . import strategies


@given(strategies.points, strategies.points, strategies.points)
def test_basic(first_point: Point,
               second_point: Point,
               third_point: Point) -> None:
    result = sign(first_point, second_point, third_point)

    assert result in {-1, 0, 1}


@given(strategies.points, strategies.points, strategies.points)
def test_permutations(first_point: Point,
                      second_point: Point,
                      third_point: Point) -> None:
    result = sign(first_point, second_point, third_point)

    points = [first_point, second_point, third_point]
    assert all(sign(*permute(points, permutation)) ==
               (result if is_even_permutation(permutation) else -result)
               for permutation in permutations(range(3)))
