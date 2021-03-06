import math
from typing import Tuple

from hypothesis import given

from tests.port_tests.hints import PortedPoint
from tests.utils import equivalence
from . import strategies


@given(strategies.points)
def test_self(point: PortedPoint) -> None:
    assert not point.distance_to(point)


@given(strategies.points_pairs)
def test_sign(points_pair: Tuple[PortedPoint, PortedPoint]) -> None:
    first_point, second_point = points_pair

    assert equivalence(first_point != second_point,
                       first_point.distance_to(second_point) > 0)


@given(strategies.points_pairs)
def test_symmetry(points_pair: Tuple[PortedPoint, PortedPoint]) -> None:
    first_point, second_point = points_pair

    assert (first_point.distance_to(second_point)
            == second_point.distance_to(first_point))


@given(strategies.points_triplets)
def test_triangle_inequality(
        points_triplet: Tuple[PortedPoint, PortedPoint, PortedPoint]
) -> None:
    first_point, second_point, third_point = points_triplet

    straight_distance = first_point.distance_to(second_point)
    workaround_distance = (first_point.distance_to(third_point)
                           + third_point.distance_to(second_point))

    assert (straight_distance <= workaround_distance
            or math.isclose(straight_distance, workaround_distance))
