from hypothesis import given

from martinez.segment import Segment
from . import strategies


@given(strategies.segments)
def test_basic(segment: Segment) -> None:
    result = segment.is_degenerate

    assert isinstance(result, bool)
