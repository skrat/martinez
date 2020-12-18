from typing import Tuple

from hypothesis import given

from martinez.utilities import find_intersections
from tests.port_tests.hints import (PortedPoint,
                                    PortedSegment)
from tests.utils import implication
from . import strategies


@given(strategies.segments_pairs)
def test_basic(segments_pair: Tuple[PortedSegment, PortedSegment]) -> None:
    first_segment, second_segment = segments_pair

    result = find_intersections(first_segment, second_segment)

    assert isinstance(result, tuple)
    assert isinstance(result[0], int)
    assert all(coordinate is None or isinstance(coordinate, PortedPoint)
               for coordinate in result[1:])


@given(strategies.segments)
def test_same_segment(segment: PortedSegment) -> None:
    result = find_intersections(segment, segment)

    assert result[0] == (1 if segment.is_degenerate else 2)
    assert result[1] == segment.source
    assert implication(segment.is_degenerate, result[-1] is None)


@given(strategies.segments)
def test_reversed(segment: PortedSegment) -> None:
    result = find_intersections(segment, segment.reversed)

    assert result[0] == (1 if segment.is_degenerate else 2)
    assert result[1] == segment.source
    assert implication(segment.is_degenerate, result[-1] is None)

def test_ulerp():
    seg_a = PortedSegment[float](PortedPoint(-1, 0, 10),
                                 PortedPoint( 1, 0, 20))
    seg_b = PortedSegment[float](PortedPoint( 0,-1, 100),
                                 PortedPoint( 0, 1, 200))
    count, pt_a, pt_b = find_intersections(
        seg_a, seg_b, ulerp=lambda a, b, t: a + t*(b-a))
    assert count == 1
    assert pt_b is None
    assert isinstance(pt_a, PortedPoint)
    assert pt_a == PortedPoint(0, 0)
    assert pt_a.user == 15
